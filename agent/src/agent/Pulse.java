package agent;

import java.lang.reflect.InvocationTargetException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Base64;
import java.util.Hashtable;

import javax.naming.NamingException;

public class Pulse {
	//keep-alive protocol
	public static Hashtable receive(ArrayList<String> response, String nonce, String etc) throws Exception {
		Hashtable resetSignal = new Hashtable();
		resetSignal.put("error",response.get(0));
		if (response.get(0) == "0x9120052102") {
			//restart interaction in case of transmission failure

			return resetSignal;
		}
		String rebuilt = new String(Util.rebuild(response));
		//clean up the response
		String cleanRebuilt = Util.clean(rebuilt);
		//convert raw array to hashtable
		try {
			byte[] decryptedBytes = Crypt.decrypt(Base64.getDecoder().decode(cleanRebuilt), nonce.getBytes());
			String decryptedResponse = new String(decryptedBytes);
			Hashtable tabifiedResponse = Util.tabify(decryptedResponse);
			
			return tabifiedResponse;
		} catch (Exception e) {
			return resetSignal;
		}
		
	}
	
	public static String make(String msgID, String cookie, String data) {
		String compiled = "." + data + ".3." + msgID;
		return compiled;	
	}
	
	public static Hashtable dispatch(String msgID, String data, String etc) throws Exception {
		int rtxc = 0;
		while (rtxc < (int) Main.config.get("maxRtxc")) {
			String nonce = Util.strand(12);
			String messageID = Util.strand(4);
			Hashtable svrParams = Netw.send("Kex",messageID,data,nonce);
			ArrayList<String> made = new ArrayList<String>();
			made.add(make(messageID,etc,data));
			//return directive check
			Hashtable txData = receive(Netw.onomancy(made),nonce,etc);
			if (!txData.containsKey("error")) {
				return txData;
			}
		}
		return new Hashtable();
	}
}

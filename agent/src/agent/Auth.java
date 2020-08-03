package agent;

import java.util.ArrayList;
import java.util.Base64;
import java.util.Hashtable;

public class Auth {
	//authentication protocol
	public static Hashtable receive(ArrayList<String> response, String nonce) throws Exception {
		if (response.get(0) == "0x9120052102") {
			//restart interaction in case of transmission failure
			Hashtable resetSignal = new Hashtable();
			resetSignal.put("error",response.get(0));
			return resetSignal;
		}
		String rebuilt = new String(Util.rebuild(response));

		//clean up the response
		String cleanRebuilt = Util.clean(rebuilt);
		//convert raw array to hashtable
		String decryptedResponse = new String(Crypt.decrypt(Base64.getDecoder().decode(cleanRebuilt), nonce.getBytes()));

		Hashtable tabifiedResponse = Util.tabify(decryptedResponse);
		return tabifiedResponse;
	}
	
	public static String passify(String nonce) throws Exception {
		String authPass = Main.config.get("password").toString();
		byte[] cryptPass = Crypt.encrypt(authPass.getBytes(), nonce.getBytes());
		return (String) Base64.getEncoder().encodeToString(cryptPass);
	}
	
	public static String make(String passBlock, String msgID) throws Exception {
		String compiled = (passBlock + "." + Main.config.get("acid").toString() + ".1." + msgID);
		return compiled;
	}
	
	public static Hashtable dispatch(String msgID, String data, String etc) throws Exception {
		//prepare the password
		int rtxc = 0;
		while (rtxc < (int) Main.config.get("maxRtxc")) {
			String nonce = Util.strand(12);
			String messageID = Util.strand(4);
			String passBlock = (String) passify(nonce);
			//receive the cookie
			Hashtable svrParams = Netw.send("Kex",messageID,passBlock,nonce);
			ArrayList<String> made = new ArrayList<String>(); 
			made.add(make(passBlock,messageID));
			Hashtable txData = receive(Netw.onomancy(made),nonce);
			if (!txData.containsKey("error")) {
				return txData;
			}
		}
		return new Hashtable();
	}
}

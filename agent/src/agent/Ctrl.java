package agent;

import java.lang.reflect.InvocationTargetException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Base64;
import java.util.Hashtable;

import javax.naming.NamingException;

public class Ctrl {
	//core command protocol

	public static Hashtable receive(ArrayList<String> response,String nonce) throws Exception {
		String rebuilt = new String(Util.rebuild(response));
		if (rebuilt == new String(new byte[] {(byte) 0x41, (byte) 0x41})) {
			Hashtable errorTable = new Hashtable();
			errorTable.put("error","0x9320085296");
			return errorTable;
		}
		//clean up the response
		String cleanRebuilt = Util.clean(rebuilt);
		//convert raw array to hashtable

		byte[] decryptedBytes = Crypt.decrypt(Base64.getDecoder().decode(cleanRebuilt), nonce.getBytes());
		String decryptedResponse = new String(decryptedBytes);
		Hashtable tabifiedResponse = Util.tabify(decryptedResponse);
		return tabifiedResponse;
	}
	
	public static String make(String cookie, String msgID) throws NoSuchAlgorithmException {
		String compiled = "." + Crypt.distort("ctrlKey") + ".5." + msgID;
		return compiled;
	}
	
	public static Hashtable dispatch(String msgID, String data, String etc) throws Exception {
		String nonce = Util.strand(12);
		String messageID = Util.strand(4);
		Hashtable svrParams = Netw.send("Kex",messageID,data,nonce);
		ArrayList<String> made = new ArrayList<String>();
		made.add(make(etc, messageID));
		return receive(Netw.onomancy(made),nonce);
	}
}

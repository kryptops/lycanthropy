package agent;

import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;

import javax.naming.NamingException;

public class Kex {
	public static String hash(String data) throws NoSuchAlgorithmException {
		String dataDigest = Util.hashify(data.getBytes());
		return dataDigest;
	}
	
	public static String make(String dataDigest, String nonce, String msgID) {
		String compiled = (nonce + "." + Main.config.get("acid").toString() + "." + dataDigest.substring(0,17) + ".4." + msgID);
		return compiled;
		
	}
	
	public static void dispatch(String msgID, String data, String etc) throws NoSuchAlgorithmException, NamingException {
		String dataDigest = hash(data);
		ArrayList<String> made = new ArrayList<String>();
		made.add(make(dataDigest,etc,msgID));
		Netw.onomancy(made);
	}

}

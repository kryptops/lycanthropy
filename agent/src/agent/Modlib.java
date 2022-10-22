package agent;

import com.sun.jna.platform.win32.WinNT;
import com.sun.jna.ptr.IntByReference;
import com.sun.jna.win32.StdCall;
import com.sun.jna.win32.StdCallLibrary;
import com.sun.jna.Native;

public class Modlib {
    public enum Win32_HotFix_Values {
        HotFixID,
        InstalledOn
    }

    public enum Win32_Service_Values {
        StartName,
        DisplayName,
        State,
        PathName,
        Description,
        StartMode
    }

    public enum Win32_UserAccount_Values {
        Name,
        SID,
        AccountType,
        Disabled,
        Description,
        Domain
    }
    public enum Win32_Product_Values {
        Name,
        Version,
        Vendor,
        PackageName,
        InstallState
    }

    public enum Win32_Autorun_Values {
        Name,
        Location,
        Command
    }

    public enum Win32_Process_Values {
        Name,
        ProcessID,
        CommandLine
    }

    public enum Win32_Environment_Values {
        Name,
        UserName,
        VariableValue
    }

    public enum Win32_Share_Values {
        Name,
        Path,
        Caption
    }

    static dbgApi32 winDbg = (dbgApi32) Native.loadLibrary("C:\\Windows\\System32\\dbghelp.dll",dbgApi32.class);
    interface dbgApi32 extends StdCallLibrary {
	    public boolean MiniDumpWriteDump(WinNT.HANDLE hProcess, long processID, WinNT.HANDLE hFile, long DumpType, long ExceptionParam, long UserStreamParam, long CallBackParam);
    }
}

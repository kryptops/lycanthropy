package agent;

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
}

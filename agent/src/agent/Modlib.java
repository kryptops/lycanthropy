package agent;

public class Modlib {
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
}

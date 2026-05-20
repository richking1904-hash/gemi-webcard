Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = WshShell.SpecialFolders("Desktop") & "\GeMi_Demo"
WshShell.Run "cmd.exe /c run_gemi.bat", 0, False
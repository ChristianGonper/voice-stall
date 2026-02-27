Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
cmd = "powershell -NoProfile -ExecutionPolicy Bypass -File """ & scriptDir & "\start_voz_tauri.ps1"" -Hidden"
shell.Run cmd, 0, False

import {xu} from "xu";
import {Program} from "../../Program.js";

export class keyCADDeluxe3D extends Program
{
	website = "https://winworldpc.com/product/keycad/30-for-windows";
	loc     = "win2k";
	bin     = "c:\\Program Files\\Creative Office\\KeyCAD Deluxe 3\\3D\\PROGRAM\\KCW3D.EXE";
	args    = r => [r.inFile()];
	osData  = ({
		script : `
			Func MainWindowOrFailure()
				WindowDismiss("Load Font", "", "{ENTER}")
				WindowDismiss("Load File", "", "{ESCAPE}")
				return WinActive("KeyCAD Deluxe 3D - ", "")
			EndFunc
			$mainWindow = CallUntil("MainWindowOrFailure", ${xu.SECOND*10})
			If Not $mainWindow Then
				Exit 0
			EndIf
			
			WindowFailure("Open File", "Error loading", 2, "{ENTER}")
			Send("!f")
			Send("E{ENTER}")
			$saveWindow = WindowRequire("Save File", "", 10)
			Send("c:\\out\\out.dxf{ENTER}")
			WinWaitClose($saveWindow, "", 10)
			WaitForStableFileSize("c:\\out\\out.dxf", ${xu.SECOND*2}, ${xu.SECOND*20})
			Send("!f")
			Send("{UP}{ENTER}")` });
	renameOut = true;
	chain     = "dexvert[asFormat:poly/dxf]";
}

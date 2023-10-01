import {xu} from "xu";
import {Program} from "../../Program.js";

export class fastCAD extends Program
{
	website  = "https://fastcad2.com/";
	unsafe   = true;
	loc      = "winxp";
	bin      = "C:\\FCAD32D\\FCW32.EXE";
	osData   = r => ({
		script : `
			WindowRequire("[CLASS:FCW32]", "", 10)
			Send("^o")
			
			$loadDrawingWindow = WindowRequire("[TITLE:Load Drawing]", "", 10)
			Send("c:\\in\\${r.inFile({backslash : true})}{ENTER}")
			WinWaitClose($loadDrawingWindow, "", 10)

			; Don't know of a better way to do this. The 'Unamed view' window is always there, and doesn't get renamed after it opens the file
			Sleep(3000)

			Send("^A")
			
			$renameSaveWindow = WindowRequire("[TITLE:Rename & Save]", "", 10)
			Send("c:\\out\\out.bmp{TAB}b{ENTER}")
			WinWaitClose($renameSaveWindow, "", 10)

			Sleep(1000)`
	});
	renameOut = true;
	chain     = "dexvert[asFormat:image/bmp]";
}

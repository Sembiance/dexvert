import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil, runUtil} from "xutil";

export class doomMUS2mp3 extends Program
{
	website   = "http://slade.mancubus.net/";
	unsafe    = true;
	loc       = "wine";
	bin       = "c:\\dexvert\\slade\\SLADE.exe";
	exclusive = true;
	args      = async r =>
	{
		// SLADE needs the file in a ZIP file
		r.zipFilePath = await fileUtil.genTempPath(r.f.root, ".zip");
		await runUtil.run("zip", ["-r", r.zipFilePath, r.inFile()], {cwd : r.f.root});
		return [r.zipFilePath];
	};
	wineData = r => ({
		script : `
			$mainWindow = WindowRequire("[TITLE:SLADE; CLASS:wxWindowNR]", "", 10)
			$entriesControl = WaitForControl($mainWindow, "", "[CLASS:wxDataView; INSTANCE:1]", ${xu.SECOND*10})
			If Not $entriesControl Then
				Exit 0
			EndIf

			$entriesPOS = ControlGetPos($mainWindow, "", $entriesControl)
			ControlFocus($mainWindow, "", $entriesControl)
			MouseClick("right", $entriesPOS[0]+20, $entriesPOS[1]+50, 1)
			Sleep(1000)
			SendSlow("{UP}{UP}{RIGHT}{ENTER}", 200)
			Sleep(1000)
			Send("^e")

			$exportWindow = WindowRequire("Export Entry", "", 10)
			Send("^ac:\\out${r.wineCounter}\\out.mid{ENTER}")
			WinWaitClose($exportWindow, "", 10)
			
			SendSlow("!fx")
			
			Func PostExtractWindows()
				WindowDismiss("Unsaved Changes", "", "n")
			EndFunc
			CallUntil("PostExtractWindows", ${xu.SECOND*2})`
	});
	renameOut = true;
	chain     = "timidity";
}

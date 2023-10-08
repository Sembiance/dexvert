import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil, runUtil} from "xutil";

export class doomMUS2mp3 extends Program
{
	website   = "http://slade.mancubus.net/";
	unsafe    = true;
	loc       = "wine";
	bin       = "c:\\dexvert\\slade\\SLADE.exe";
	exclusive = "wine";
	notes     = "This is very flaky. Always has been. SLADE is open source and runs on Linux, so in theory with some work I could build a CLI to convert the .mus to .mid more reliably.";
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
			Sleep(1500)
			SendSlow("{UP}{UP}{RIGHT}{ENTER}", 200)
			Sleep(1500)
			Send("^e")

			$exportWindow = WindowRequire("Export Entry", "", 10)
			SendSlow("^ac:\\out${r.wineCounter}\\out.mid{ENTER}")
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

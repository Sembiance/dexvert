import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

export class hyperReader4 extends Program
{
	website  = "https://discmaster.textfiles.com/browse/21823/Pegasus_Windows_20.iso/pegasus/w_editor/hrw40.zip";
	loc      = "win2k";
	bin      = "c:\\dexvert\\hrw40\\HRW.EXE";
	unsafe   = true;
	args     = r => [r.inFile()];
	osData   = () => ({
		dontMaximize : true,
		script : `
			Func MainWindowOrFailure()
				WindowFailure("Error", "", -1, "{ESCAPE}")
				WindowFailure("HyperReader!", "HyperReader cannot read", -1, "{ENTER}")
				return WinActive("[CLASS:HRMain]", "")
			EndFunc
			$mainWindow = CallUntil("MainWindowOrFailure", ${xu.SECOND*10})
			If Not $mainWindow Then
				Exit 0
			EndIf

			Func SavePage($num)
				Send("+{F2}")
				$gotoWindow = WindowRequire("Goto", "", 5)
				Send($num & "{ENTER}")
				WinWaitClose($gotoWindow, "", 5)
				; If goto window remains, we're at the end of the document
				If WinActive($gotoWindow) Then
					Send("{ESCAPE}")
					WinWaitClose($gotoWindow, "", 5)
					return 0
				EndIf
				WinWaitActive($mainWindow, "", 5)
				Send("^e");
				$saveWindow = WindowRequire("Export Filename", "", 5)
				$saveFilePath = "c:\\OUT\\P" & $num & ".TXT"
				Send($saveFilePath & "{ENTER}")
				WinWaitClose($saveWindow, "", 5)
				WaitForStableFileSize($saveFilePath, ${xu.SECOND}, ${xu.SECOND*4})
				$fileSize = FileGetSize($saveFilePath)
				If $fileSize < 3 Then
					FileDelete($saveFilePath)
					return 0
				EndIf
				return 1
			EndFunc

			; Starting at number 1, loop up to 999 until SavePage returns 0
			For $i = 1 To 999
				If Not SavePage($i) Then
					ExitLoop
				EndIf
			Next

			Send("!f")
			Sleep(500)
			Send("x")
			WindowDismissWait("HyperReader!", "Leave Bookmark", 5, "n")
			WindowDismissWait("HyperReader!", "Thank you for allowing us", 5, "{ENTER}")
			`
	});
	postExec = async r =>
	{
		const pageFilePaths = await fileUtil.tree(r.outDir({absolute : true}), {nodir : true, regex : /P\d+\.TXT$/});
		await fileUtil.concat(pageFilePaths.sortMulti([pageFilePath => +path.basename(pageFilePath).match(/^P(?<num>\d+)\.TXT$/).groups.num]), await r.outFile("out.txt", {absolute : true}), {seperator : "\n\n\n"});
		await pageFilePaths.parallelMap(async pageFilePath => await fileUtil.unlink(pageFilePath));
	};
	renameOut = true;
}

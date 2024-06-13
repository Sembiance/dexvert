import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

export class hyperReader3 extends Program
{
	website  = "https://discmaster.textfiles.com/browse/21823/Pegasus_Windows_20.iso/pegasus/w_editor/hrw40.zip";
	loc      = "win2k";
	bin      = "c:\\WINNT\\system32\\cmd.exe";	//c:\\dexvert\\HRREAD33\\HR.EXE
	unsafe   = true;
	args     = r => [r.inFile()];
	osData   = r => ({
		dontMaximize : true,
		cwd : "c:\\dexvert\\HRREAD33",
		script : `
			$mainWindow = WindowRequire("c:\\WINNT\\system32\\cmd.exe", "", 10)
			Send("HR.EXE c:\\in\\${r.inFile({backslash : true})}")
			Send("{ENTER}")
			Sleep(3000)

			Func SavePage($num)
				Send("+{F2}")
				Sleep(200)
				SendSlow("{BS}{BS}" & $num & "{ENTER}")
				Sleep(750)
				Send("^e");
				Sleep(1000)
				SendSlow("{BS}{BS}{BS}{BS}{BS}")
				$filename = "P" & $num & ".TXT";
				Send($filename)
				Send("{ENTER}")
				$saveFilePath = "c:\\OUT\\" & $filename;
				WaitForStableFileSize($saveFilePath, ${xu.SECOND}, ${xu.SECOND*4})
				$fileSize = FileGetSize($saveFilePath)
				If $fileSize = 0 Then
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
			Next`
	});
	postExec = async r =>
	{
		const pageFilePaths = await fileUtil.tree(r.outDir({absolute : true}), {nodir : true, regex : /P\d+\.TXT$/});
		await fileUtil.concat(pageFilePaths.sortMulti([pageFilePath => +path.basename(pageFilePath).match(/^P(?<num>\d+)\.TXT$/).groups.num]), await r.outFile("out.txt", {absolute : true}), {seperator : "\n\n\n"});
		await pageFilePaths.parallelMap(async pageFilePath => await fileUtil.unlink(pageFilePath));
	};
	renameOut = true;
}

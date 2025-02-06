import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class decomposeSGS extends Program
{
	website = "https://www.logipole.com/konvertor-en.htm";
	loc     = "win7";
	bin     = "c:\\dexvert\\DecomposeSGS\\DecomposeSGS.exe";
	osData  = r => ({
		scriptPre : `
			FileCopy("c:\\in\\${path.basename(r.inFile())}", "c:\\out\\${path.basename(r.inFile())}");`,
		script : `
			$mainWindow = WindowRequire("Decompose SGS.DAT", "", 10)
			Send("c:\\out\\${path.basename(r.inFile())}")
			SendSlow("{TAB}{TAB}{TAB}")
			SendSlow("{DOWN}{DOWN}")
			SendSlow("{TAB}{END}")
			SendSlow("+{TAB}+{TAB}")

			Local $lastCount = DirFileCount("c:\\out")
			Send("{ENTER}")

			Local $stableCountTimer = GetTime()
			Local $stableTimer = GetTime()
			Do
				Sleep(50)

				$curCount = DirFileCount("c:\\out")
				If $curCount <> $lastCount Then
					$lastCount = $curCount
					$stableTimer = GetTime()
				ElseIf TimeDiff($stableTimer) > ${xu.SECOND*30} Then
					ExitLoop
				EndIf
			Until TimeDiff($stableCountTimer) > ${xu.MINUTE*30}
			FileDelete("c:\\out\\${path.basename(r.inFile())}")`
	});
	renameOut = true;
}

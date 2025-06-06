import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class installShieldSelfExtractor extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	unsafe  = true;
	loc     = "win2k";
	bin     = r => `c:\\in\\${path.basename(r.inFile())}`;
	osData  = ({
		alsoKill : ["SETUP.EXE"],
		scriptPre : `
			DirEmpty("c:\\WINNT\\Temp")`,
		script : `
			Func WaitForFiles()
				WindowDismiss("InstallShield Self-extracting EXE", "", "Y")
				return FileExists("c:\\WINNT\\Temp\\_ISTMP0.DIR") And DirFileCount("c:\\WINNT\\Temp\\_ISTMP0.DIR") > 0
			EndFunc
			$foundDir = CallUntil("WaitForFiles", ${xu.MINUTE})
			If Not $foundDir Then
				Exit 0
			EndIf
			WaitForStableDirCount("c:\\WINNT\\Temp\\_ISTMP0.DIR", ${xu.SECOND*10}, ${xu.MINUTE*2})
			DirCopyContents("c:\\WINNT\\Temp", "c:\\out")

			Local $plist = ProcessList()
			For $i = 1 To $plist[0][0]
				If StringLower(StringLeft($plist[$i][0], 4)) = "_ins" Then
					ProcessClose($plist[$i][1])
				EndIf
			Next
		`
	});
	renameOut = false;
}

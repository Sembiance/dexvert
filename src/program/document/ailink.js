import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class ailink extends Program
{
	website = "https://ai.ansible.uk/ailink.html";
	bin     = "c:\\dexvert\\ailink\\AILINK.EXE";
	loc     = "win2k";
	args    = () => [];
	osData  = r => ({
		script : `
			$mainWindow = WindowRequire("LocoScript conversion", "", 10)
			Send("^o")
			$selectWindow = WindowRequire("Select LocoScript file", "", 10)
			Send("c:\\in\\${path.basename(r.inFile())}{ENTER}")
			WinWaitClose($selectWindow, "", 10)
			WindowFailure("Warning", "", 3, "{ENTER}")
			WaitForStableFileSize("c:\\out\\${path.basename(r.inFile(), path.extname(r.inFile()))}_${path.extname(r.inFile()).substring(1)}.rtf", ${xu.SECOND*2}, ${xu.SECOND*10})
			Send("!f")
			Send("x")`
	});
	renameOut = true;
	chain     = "dexvert[asFormat:document/rtf]";
}

import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class sfpack extends Program
{
	website = "https://archive.org/details/SFPack";
	bin     = "c:\\dexvert\\SFPack\\SFPACK.EXE";
	args    = r => [r.inFile()];
	loc     = "win2k";
	osData  = r => ({
		script : `
			$mainWindow = WindowRequire("SFPack", "", 10)
			
			Send("^f")
			$browseWindow = WindowRequire("Browse for Folder", "", 10)
			Send("out")
			Send("{ENTER}")
			WinWaitClose($browseWindow, "", 5)

			Send("!f")
			Send("g")

			WaitForStableFileSize("c:\\out\\${path.basename(r.inFile(), path.extname(r.inFile()))}.sf2", ${xu.SECOND*3}, ${xu.SECOND*15})

			Send("!f")
			Send("x")
			
			WinWaitClose($mainWindow, "", 3)`
	});
	renameOut = true;
}

import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class painterClassic extends Program
{
	website = "https://archive.org/details/Painter_Classic_Z-PTC-C10-R-001_MetaCreations_1998/";
	unsafe  = true;
	loc     = "win7";
	bin     = "c:\\Program Files\\Painter Classic\\PClassic.exe";
	args    = r => [r.inFile()];
	osData  = r => ({
		script : `
			$mainWindow = WindowRequire("MetaCreations Painter Classic", "${path.basename(r.inFile())}", 20)
			Sleep(500)

			SendSlow("!fa{ENTER}")

			$saveWindow = WindowRequire("Save Image As", "", 10)
			SendSlow("c:\\out\\out.TIF{TAB}t")
			Sleep(500)
			Send("{ENTER}")
			WinWaitClose($saveWindow, "", 5)

			WaitForStableFileSize("c:\\out\\out.TIF", ${xu.SECOND*3}, ${xu.SECOND*15})

			Send("^q")
			FileDelete("c:\\out\\PREVIEW.PIX")
			WinWaitClose($mainWindow, "", 10)`
	});
	renameOut = true;
	chain     = "deark[module:tiff][noThumbs]";
}

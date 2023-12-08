import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class directorCastRipper10 extends Program
{
	website   = "https://github.com/n0samu/DirectorCastRipper";
	loc       = "wine";
	bin       = "DirectorCastRipper_D10/DirectorCastRipper.exe";
	exclusive = "wine";
	args      = r => ["--files", `c:\\in${r.wineCounter}\\${path.basename(r.inFile())}`, "--output-folder", `c:\\out${r.wineCounter}`, "--include-names", "--dismiss-dialogs"];
	wineData  = ({
		timeout : xu.MINUTE*5
	});
	renameOut = false;
}

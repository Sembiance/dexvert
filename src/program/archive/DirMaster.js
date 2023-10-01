import {xu} from "xu";
import {Program} from "../../Program.js";

export class DirMaster extends Program
{
	website  = "https://style64.org/dirmaster";
	loc      = "wine";
	bin      = "c:\\Program Files\\Style\\DirMaster\\DirMaster.exe";
	flags   = {
		timeout : "Stop after X ms. Default: 3 minutes"
	};
	args     = r => ["--exportall", r.inFile()];
	cwd      = r => r.outDir();
	wineData = r => ({
		timeout : (+(r.flags.timeout || xu.MINUTE*3))
	});
	renameOut = {
		alwaysRename : true,
		regex        : /(?<name>.+)\.prg$/,
		renamer      :
		[
			({suffix}, {name}) => [name, suffix]
		]
	};
}

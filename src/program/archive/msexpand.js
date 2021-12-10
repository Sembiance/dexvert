import {Program} from "../../Program.js";

export class msexpand extends Program
{
	website       = "http://gnuwin32.sourceforge.net/packages/mscompress.htm";
	package       = "app-arch/mscompress";
	bin           = "msexpand";
	args          = r => [r.inFile()];
	cwd           = r => r.outDir();
	mirrorInToCWD = true;
	renameOut     = {
		alwaysRename : true,
		renamer      : [({newName, suffix, originalExt}) => [newName, suffix, originalExt.endsWith("_") ? originalExt.slice(0, -1) : originalExt]]
	};
}

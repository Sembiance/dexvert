import {Program} from "../../Program.js";

export class msexpand_win2k extends Program
{
	website      = "https://www.computerhope.com/expandhl.htm";
	notes        = "Warning: EXPAND.EXE will just 'copy' the source file over to the destination if it can't extract it.";
	unsafe       = true;
	loc          = "win2k";
	bin          = "c:\\WINNT\\system32\\expand.exe";
	args         = r => [r.inFile(), "c:\\out\\"];
	checkForDups = true;
	renameOut    = {
		alwaysRename : true,
		renamer      : [({newName, suffix, originalExt}) => [newName, suffix, originalExt.endsWith("_") ? originalExt.slice(0, -1) : originalExt]]
	};
}

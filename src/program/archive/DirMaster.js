import {Program} from "../../Program.js";

export class DirMaster extends Program
{
	website  = "https://style64.org/dirmaster";
	loc      = "winxp";
	bin      = "DirMaster.exe";
	args     = r => ["--exportall", r.inFile()];
	qemuData = ({cwd : "c:\\out"});
	renameOut = {
		alwaysRename : true,
		regex        : /(?<name>.+)\.prg$/,
		renamer      :
		[
			({suffix}, {name}) => [name, suffix]
		]
	};
}

// NOTE: Node version used to rename all files, sticking any 1 to 3 digit extension prefix at the end as a suffix instead.
// I have chosen not to do that in this new deno version, as a format can matchPreExt if needed

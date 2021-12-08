import {Program} from "../../Program.js";

export class amosbank extends Program
{
	website          = "https://github.com/dschwen/amosbank";
	package          = "dev-lang/amosbank";
	bin              = "amosbank";
	mirrorInToCWD    = true;
	cwd              = r => r.outDir();
	args             = r => [r.inFile()];
	filenameEncoding = "iso-8859-1";	// AmigaOS uses this: http://lclevy.free.fr/adflib/adf_info.html#p54
	chain            = "sox";
	renameOut        = {
		alwaysRename : true,
		regex        : /.+?(?<num>\.\d+)\.(?<name>.+)(?<ext>\.wav)$/,
		renamer      :
		[
			({suffix}, {name, ext}) => [name, suffix, ext],
			({suffix, numFiles}, {name, num, ext}) => [num.padStart(numFiles.toString().length, "0"), name, suffix, ext]
		]
	};
}

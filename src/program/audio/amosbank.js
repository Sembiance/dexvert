import {Program} from "../../Program.js";

export class amosbank extends Program
{
	website        = "https://github.com/dschwen/amosbank";
	package        = "dev-lang/amosbank";
	bin            = "amosbank";
	symlinkInToCWD = true;
	cwd            = r => r.outDir();
	args           = r => [r.inFile()];
	chain          = "ffmpeg[outType:mp3]";
	renameOut      = {
		alwaysRename : true,
		regex        : /.+?(?<num>\.\d+)\.(?<name>.+)(?<ext>\.wav)$/,
		renamer      :
		[
			({suffix}, {name, ext}) => [name, suffix, ext],
			({suffix, numFiles}, {name, num, ext}) => [num.padStart(numFiles.toString().length, "0"), name, suffix, ext]
		]
	};
}

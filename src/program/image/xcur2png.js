import {Program} from "../../Program.js";

export class xcur2png extends Program
{
	website   = "https://github.com/eworm-de/xcur2png";
	package   = "media-gfx/xcur2png";
	bin       = "xcur2png";
	args      = r => ["--directory", r.outDir(), r.inFile()];
	renameOut = {
		alwaysRename : true,
		regex        : /.+_(?<num>\d+)\.png$/,
		renamer      : [({newName, newExt}, {num}) => [newName, "_", num, newExt]]
	};
}

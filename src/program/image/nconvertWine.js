import {xu} from "xu";
import {Program} from "../../Program.js";

export class nconvertWine extends Program
{
	website   = "https://discmaster.textfiles.com/browse/23608/PCWorld0410.iso/redakcyjne/programy/XnView%201.97/XnView-win-full.zip";
	loc       = "wine";
	bin       = "c:\\dexvert\\XnView\\nconvert.exe";
	outExt    = ".png";
	args      = async r => ["-out", "png", "-o", await r.outFile("out.png"), r.inFile()];
	renameOut = {
		alwaysRename : true,
		regex        : /^out-(?<num>\d+)(?<ext>\.[^.]+)$/,	// this regex assumes the input filename doesn't have an underscore
		renamer      :
		[
			({numFiles}, {num, ext}) => [num.padStart(numFiles.toString().length, "0"), ext],
			({newName, newExt}) => [newName, newExt]
		]
	};
}

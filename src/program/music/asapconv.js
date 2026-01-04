import {Program} from "../../Program.js";

export class asapconv extends Program
{
	website   = "http://asap.sourceforge.net/";
	package   = "media-sound/asap";
	bin       = "asapconv";
	args      = async r => ["-o", await r.outFile("outfile%s.wav"), r.inFile()];
	renameOut = {
		regex        : /outfile(?<songNum>\d+)(?<ext>\.wav)$/,
		renamer      :
		[
			({suffix, newName, numFiles}, {songNum, ext}) => [newName, " ", songNum.padStart(numFiles.toString().length, "0"), suffix, ext]
		]
	};
	chain = "sox[type:wav]";
}

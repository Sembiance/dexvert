import {Program} from "../../Program.js";

export class sidplay2 extends Program
{
	website = "http://sidplay2.sourceforge.net/";
	package = "media-sound/sidplay";
	flags   = {
		subSong    : "Specify which sub song to convert, zero based. Default: 1",
		songLength : "Duration of time to play the SID song. Default: Let sidplay2 decide"
	};
	bin = "sidplay2";
	args = async r =>
	{
		const a = [`-w${await r.outFile(`outfile_${(r.flags.subSong || 1)}.wav`)}`, `-o${r.flags.subSong || 1}`];
		if(r.flags.songLength)
			a.push(`-t${r.flags.songLength}`);
		a.push(r.inFile());

		return a;
	};
	renameOut = {
		alwaysRename : true,
		regex        : /outfile_(?<songNum>\d+)(?<ext>\.wav)$/,
		renamer      :
		[
			({suffix, newName, numFiles}, {songNum, ext}) => [newName, " ", songNum.padStart(numFiles.toString().length, "0"), suffix, ext]
		]
	};
	chain = "sox";
}

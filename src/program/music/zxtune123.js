import {Program} from "../../Program.js";

export class zxtune123 extends Program
{
	website       = "https://zxtune.bitbucket.io/";
	gentooPackage = "media-sound/zxtune";
	gentooOverlay = "dexvert";
	bin           = "zxtune123";
	args          = r => ["--silent", "--file", r.inFile(), `--wav=filename=${r.outDir()}/[Fullpath].wav`];
	chain         = "ffmpeg[outType:mp3]";
	renameOut      = {
		alwaysRename : true,
		regex        : /_#(?<songNum>\d+)(?<ext>\.wav)$/,
		renamer      :
		[
			({suffix, newName, numFiles}, {songNum, ext}) => [newName, " ", songNum.padStart(numFiles.toString().length, "0"), suffix, ext],
			({suffix, newName, newExt}) => [newName, suffix, newExt],
			({fn}) => [fn]
		]
	};
}

import {Program} from "../../Program.js";

export class zxtune123 extends Program
{
	website   = "https://zxtune.bitbucket.io/";
	package   = "media-sound/zxtune";
	bin       = "zxtune123";
	args      = r => ["--silent", "--file", r.inFile(), `--wav=filename=${r.outDir()}/[Fullpath].wav`];
	renameOut = {
		alwaysRename : true,
		regex        : /_(?:(?:#(?<songNum>\d+))|(?:\+(?<name>.+)))(?<ext>\.wav)$/,
		renamer      :
		[
			({suffix, newName, numFiles}, {songNum, ext}) => [newName, " ", songNum.padStart(numFiles.toString().length, "0"), suffix, ext],
			({suffix, newName}, {name, ext}) => (name && name.length>0 ? [newName, " ", name, suffix, ext] : ""),
			({suffix, newName, newExt}) => [newName, suffix, newExt]
		]
	};
	chain = "sox";
}

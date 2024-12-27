import {xu} from "xu";
import {Program} from "../../Program.js";

export class zxtune123 extends Program
{
	website = "https://zxtune.bitbucket.io/";
	package = "media-sound/zxtune";
	flags   = {
		trimSilence : "Trim silence from the beginning and end of the audio",
		largeQuota  : "Some multi-track formats like nsf just produce a lot of audio, so we make a very large disk quota check for those"
	};

	// Some files like digitalSymphony/vath will just create massive multi-gigabyte files, it's all valid audio, but no way to instruct it to stop sooner
	diskQuota = r => (r.flags.largeQuota ? xu.GB*4 : xu.MB*500);

	bin        = "zxtune123";
	bruteFlags = { audio : {} };
	args       = r => ["--silent", "--file", r.inFile(), `--wav=filename=${r.outDir()}/[Fullpath].wav`];
	runOptions = ({timeout : xu.MINUTE*5});	// some files will play and loop forever (music/mkJamz/pcs2 1.mkj)
	renameOut  = {
		alwaysRename : true,
		regex        : /_(?:(?:#(?<songNum>\d+))|(?:\+(?<name>.+)))(?<ext>\.wav)$/,
		renamer      :
		[
			({suffix, newName, numFiles}, {songNum, ext}) => [newName, " ", songNum.padStart(numFiles.toString().length, "0"), suffix, ext],
			({suffix, newName}, {name, ext}) => (name && name.length>0 ? [newName, " ", name, suffix, ext] : ""),
			({suffix, newName, newExt}) => [newName, suffix, newExt]
		]
	};
	chain = r => `ffmpeg[outType:wav] -> sox[maxDuration:${xu.MINUTE*10}]${r.flags.trimSilence ? "[trimSilence]" : ""}`;
}

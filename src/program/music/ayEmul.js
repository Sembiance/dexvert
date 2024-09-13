import {xu} from "xu";
import {Program} from "../../Program.js";

export class ayEmul extends Program
{
	website    = "https://bulba.untergrund.net/emulator_e.htm";
	bin        = Program.binPath("Ay_Emul29.src/lib/x86_64-linux/Ay_Emul");
	flags   = {
		subSong   : "Specify which sub song to convert, zero based. Default: 0",
		songName  : "Specify the song name for the sub song being converted",
		songCount : "Specify the total number of sub songs in the file"
	};
	args       = r => ["-dmono", `${r.inFile({absolute : true})}${r.flags.subSong ? `:${r.flags.subSong}` : ""}`];		// -dmixer -hAYACB also sounds nice if you want a little bit of stereo mixing
	cwd        = r => r.outDir();
	runOptions = r => ({virtualX : true, timeout : xu.SECOND*20, env : {outName : `${r.flags.subSong || "output"}.wav`, outDir : r.outDir({absolute : true, trailingSlash : true})}});
	exclusive  = "Ay_Emul";	// despite having unique home directories with unique config directories, Ay_Emul still refuses to run correctly if more than one instance is running at a time

	notes      = "This program has been modified by dexvert to automatically convert to WAV on launch and immediately exit";
	renameOut  = {
		alwaysRename : true,
		renamer      :
		[
			({r}) => ([r.flags.subSong.toString().padStart(r.flags.songCount.toString().length, "0"), r.flags.songName?.length ? " - " : "", r.flags.songName || "", ".wav"]),
			({newName}) => [newName]
		]
	};
	chain = "sox";
}

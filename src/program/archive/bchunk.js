import {Program} from "../../Program.js";
import {base64Decode} from "std";

export class bchunk extends Program
{
	website = "http://he.fi/bchunk/";
	package = "app-cdr/bchunk";
	unsafe  = true;
	flags   = {
		cueFilePath : "Absolute path to the cue file. BASE64 encoded so it works in the flags. REQUIRED",
		swapByteOrder : "If set to true, will swap the byte ordering for WAVs extracted from audio tracks with bchunk"
	};
	bin  = "bchunk";
	cwd  = r => r.outDir();
	args = r =>
	{
		const a = ["-w"];
		if(r.flags.swapByteOrder)
			a.push("-s");

		a.push(r.inFile(), new TextDecoder().decode(base64Decode(r.flags.cueFilePath)), `${r.f.input.name}-`);
		return a;
	};

	// Convert with dexvert any resulting files from bchunk. This includes .iso and .wav files
	chain     = "dexvert[skipVerify][bulkCopyOut]";
	renameOut = true;
}

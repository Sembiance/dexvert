import {Program} from "../../Program.js";

export class bchunk extends Program
{
	website = "http://he.fi/bchunk/";
	package = "app-cdr/bchunk";
	unsafe  = true;
	flags   = {
		cueFilePath : "Absolute path to the cue file. REQUIRED",
		swapByteOrder : "If set to true, will swap the byte ordering for WAVs extracted from audio tracks with bchunk"
	};
	bin  = "bchunk";
	cwd  = r => r.outDir();
	args = r =>
	{
		const a = ["-w"];
		if(r.flags.swapByteOrder)
			a.push("-s");
		a.push(r.inFile(), r.flags.cueFilePath, `${r.f.input.name}-`);
		return a;
	};

	// Convert with dexvert any resulting files from bchunk. This includes .iso and .wav files
	chain = "dexvert";
}

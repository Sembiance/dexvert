import {Program} from "../../Program.js";
import {base64Decode} from "std";
import {fileUtil} from "xutil";

export class bchunk extends Program
{
	website = "http://he.fi/bchunk/";
	package = "app-cdr/bchunk";
	unsafe  = true;
	flags   = {
		cueFilePath   : "Absolute path to the cue file. BASE64 encoded so it works in the flags. REQUIRED",
		swapByteOrder : "If set to true, will swap the byte ordering for WAVs extracted from audio tracks with bchunk",
		forceMode1    : "If set to true, the CUE file will be modified from MODE2/2352 to MODE1/2352"
	};
	bin  = "bchunk";
	cwd  = r => r.outDir();
	args = async r =>
	{
		const a = ["-w"];
		if(r.flags.swapByteOrder)
			a.push("-s");

		let cueFilePath = new TextDecoder().decode(base64Decode(r.flags.cueFilePath));
		if(r.flags.forceMode1)
		{
			r.tmpCueFilePath = await fileUtil.genTempPath(undefined, ".cue");
			await Deno.copyFile(cueFilePath, r.tmpCueFilePath);
			await fileUtil.searchReplace(r.tmpCueFilePath, "MODE2/2352", "MODE1/2352");
			cueFilePath = r.tmpCueFilePath;
		}

		a.push(r.inFile(), cueFilePath, `${r.f.input.name}-`);
		return a;
	};

	postExec = async r =>
	{
		if(r.tmpCueFilePath)
			await fileUtil.unlink(r.tmpCueFilePath);
	};

	// Multi-track bin/cue with seperate bins per audio track produces 44 byte sized wavs with nothing but silence in them
	verify = (r, dexFile) => dexFile.ext.toLowerCase()!==".wav" || dexFile.size!==44;

	// Convert with dexvert any resulting files from bchunk. This includes .iso and .wav files
	chain     = "dexvert[skipVerify][bulkCopyOut]";
	renameOut = true;
}

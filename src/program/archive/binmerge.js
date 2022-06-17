import {Program} from "../../Program.js";
import {base64Decode, path} from "std";

export class binmerge extends Program
{
	website = "https://github.com/putnam/binmerge";
	package = "app-arch/binmerge";
	unsafe  = true;
	flags   = {
		cueFilePath : "Absolute path to the cue file. BASE64 encoded so it works in the flags. REQUIRED"
	};
	bin       = "binmerge";
	cwd       = r => path.dirname(new TextDecoder().decode(base64Decode(r.flags.cueFilePath)));
	args      = r => ["-o", r.outDir({absolute : true}), path.basename(new TextDecoder().decode(base64Decode(r.flags.cueFilePath))), "MergedBINCUE"];
	renameOut = false;
}

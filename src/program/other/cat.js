import {xu} from "xu";
import {Program} from "../../Program.js";
import {base64Decode} from "std";

export class cat extends Program
{
	website = "https://www.gnu.org/software/coreutils/";
	package = "sys-apps/coreutils";
	flags   = {
		inputFilePaths : "Base64 encoded JSON encoded array of absolute file paths to concatenate. REQUIRED",
		outputFilename : "Output filename. REQUIRED"
	};
	bin        = "cat";
	args       = r => xu.parseJSON(new TextDecoder().decode(base64Decode(r.flags.inputFilePaths)));
	runOptions = async r => ({stdoutFilePath : await r.outFile(r.flags.outputFilename)});
	renameOut  = false;
}

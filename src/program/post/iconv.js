import {xu} from "xu";
import {Program} from "../../Program.js";

export class iconv extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	flags   = {
		fromEncoding : "Encoding to translate from. REQUIRED",
		toEncoding   : "Encoding to translate into. Default: UTF-8"
	};
	bin        = "iconv";
	args       = r => ["-f", r.flags.fromEncoding, "-t", r.flags.toEncoding || "UTF-8", r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.txt")});
	renameOut  = true;
}

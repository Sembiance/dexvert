import {Program} from "../../Program.js";

export class zipInfo extends Program
{
	website    = "http://infozip.sourceforge.net/";
	package    = "app-arch/unzip";
	bin        = "unzip";
	args       = r => ["-qz", r.inFile()];
	runOptions = ({stdoutEncoding : "CP437"});
	post       = r =>
	{
		// Check to see if we have an archive comment
		if(r.stdout.trim().length>0 && !r.stdout.includes("End-of-central-directory signature not found"))
			r.meta.comment = r.stdout;	// Don't trim, to preserve whitespace
	};
	renameOut = false;
}

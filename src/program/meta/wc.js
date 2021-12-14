import {xu} from "xu";
import {Program} from "../../Program.js";

export class wc extends Program
{
	website    = "https://www.gnu.org/software/coreutils/";
	package    = "sys-apps/coreutils";
	bin        = "wc";
	args       = r => ["-l", r.inFile()];
	post       = r =>
	{
		const lineCount = +(r.stdout.split(" ")[0]);
		if(!isNaN(lineCount))
			r.meta.lineCount = lineCount;
	};
	renameOut = false;
}

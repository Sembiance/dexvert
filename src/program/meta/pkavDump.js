import {xu} from "xu";
import {Program} from "../../Program.js";

export class pkavDump extends Program
{
	bin  = "python3";
	args = r => [Program.binPath("pkavDump.py"), "--contentOnly", r.inFile()];
	post = r =>
	{
		const meta = {};
	
		if(r.stdout.trim().length)
			meta.pkavDump = r.stdout.trim();

		Object.assign(r.meta, meta);
	};
	renameOut = false;
}

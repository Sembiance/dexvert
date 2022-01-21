import {Program} from "../../Program.js";

export class dd extends Program
{
	website = "https://www.gnu.org/software/coreutils/";
	package = "sys-apps/coreutils";
	flags   = {
		bs   : "Byte size to set. Default: 1",
		skip : "How many bytes to skip"
	};
	bin  = "dd";
	args = async r =>
	{
		const a = [];
		a.push(`bs=${r.flags.bs || 1}`);
		if(r.flags.skip)
			a.push(`skip=${r.flags.skip}`);
		
		a.push(`if=${r.inFile()}`);
		a.push(`of=${await r.outFile("out")}`);
		return a;
	};
	renameOut = true;
}

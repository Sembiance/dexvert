import {Program} from "../../Program.js";

export class dd extends Program
{
	website = "https://www.gnu.org/software/coreutils/";
	package = "sys-apps/coreutils";
	flags   = {
		bs   : "Byte size to set",
		skip : "How many bytes to skip"
	};
	bin  = "dd";
	args = async r =>
	{
		const a = [];
		if(r.flags.bs)
			a.push(`bs=${r.flags.bs}`);
		if(r.flags.skip)
			a.push(`skip=${r.flags.skip}`);
		
		a.push(`if=${r.inFile()}`);
		a.push(`of=${await r.outFile("out")}`);
		return a;
	};
	renameOut = true;
}

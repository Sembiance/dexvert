import {Program} from "../../Program.js";

export class unshield extends Program
{
	website = "https://github.com/twogood/unshield";
	package = "app-arch/unshield";
	flags   = {
		oldCompression : "Set to true to instruct unshield to decompress using the old compression method. Default: false"
	};
	bin  = "unshield";
	args = r => [...(r.flags.oldCompression ? ["-O"] : []), "-d", r.outDir(), "x", r.inFile()];
}

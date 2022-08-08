import {Program} from "../../Program.js";

export class ytnef extends Program
{
	website    = "https://github.com/Yeraze/ytnef";
	package    = "net-mail/ytnef";
	bin        = "ytnef";
	args       = r => ["-F", "-f", r.outDir(), r.inFile()];
	renameOut  = false;
	chain      = "?dexvert[asFormat:document/rtf]";
	chainCheck = (r, chainFile) => [".rtf"].includes(chainFile.ext.toLowerCase());
}

import {Program} from "../../Program.js";

export class WoW extends Program
{
	website = "http://aminet.net/package/util/conv/WoW";
	unsafe  = true;
	flags   = {
		outType : `Which format to convert into (asc, html, rtf). Default is: rtf`
	};
	bin     = "vamos";
	args    = async r => [...Program.vamosArgs("WoW"), `-${r.flags.outType || "rtf"}`, r.inFile(), await r.outFile(`out.${r.flags.outType==="asc" ? "txt" : (r.flags.outType || "rtf")}`)];
	
	// When WoW fails, it produces files with just a few newlines in it, so we filter those out here with a reasonable size check
	verify    = (r, dexFile) => dexFile.size>=32;
	chain     = r => ((r.flags.outType || "rtf")==="rtf" ? "dexvert[asFormat:document/rtf]" : null);
	renameOut = true;
}

import {xu} from "xu";
import {Program} from "../../Program.js";

export class pv extends Program
{
	website   = "https://github.com/Sembiance/dexvert/tree/master/dos/PV.EXE";
	loc       = "dos";
	bin       = "PV.EXE";
	unsafe    = true;
	args      = r => [r.inFile(), r.outDir(), "/c"];
	dosData   = ({
		timeout : xu.MINUTE,
		keys    : [{delay : xu.SECOND*2}, "y"]
	});
	renameOut = true;
	chain     = "dexvert[asFormat:image/pcx]";
}

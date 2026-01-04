import {Program} from "../../Program.js";

export class lbplay extends Program
{
	website   = "https://www.rarewares.org/rrw/lbpack.php";
	unsafe    = true;
	loc       = "dos";
	bin       = "LB/LBPLAY.EXE";
	args      = async r => [r.inFile({backslash : true}), await r.outFile("out.wav", {backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = true;
	chain     = "sox[type:wav]";
}

import {Program} from "../../Program.js";

export class vocpak extends Program
{
	website   = "https://www.rarewares.org/rrw/vocpack.php";
	unsafe    = true;
	loc       = "dos";
	bin       = "VOCPAK20/UNVP10.EXE";
	args      = async r => [r.inFile({backslash : true}), await r.outFile("out.voc", {backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = true;
	chain     = "sox";
}

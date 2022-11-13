import {Program} from "../../Program.js";

export class sonarcx extends Program
{
	website   = "https://www.rarewares.org/rrw/sonarc.php";
	unsafe    = true;
	loc       = "dos";
	bin       = "SONARCX.EXE";
	args      = async r => [r.inFile({backslash : true}), await r.outFile("out.wav", {backslash : true})];
	chain     = "sox";
	renameOut = true;
}

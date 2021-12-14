import {Program} from "../../Program.js";

export class pplx extends Program
{
	website       = "http://files.mpoli.fi/unpacked/tlr/pcboard_bbs_utilities/agsppx20.zip/";
	loc           = "dos";
	bin           = "PPLX.EXE";
	args          = r => [r.inFile({backslash : true})];
	cwd           = r => r.outDir();
	mirrorInToCWD = "copy";
	dosData       = () => ({runIn : "out"});
	renameOut     = true;
}

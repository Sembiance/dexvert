import {Program} from "../../Program.js";

export class GRZip extends Program
{
	website   = "https://www.sac.sk/files.php?d=7&l=";
	loc       = "dos";
	bin       = "GRZIP.EXE";
	args      = r => ["e", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}

import {xu} from "xu";
import {Program} from "../../Program.js";

export class limit extends Program
{
	website   = "http://cd.textfiles.com/nightowl/nopv13/014A/LIMIT12.ZIP";
	loc       = "dos";
	bin       = "LIMIT.EXE";
	args      = r => ["e", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}

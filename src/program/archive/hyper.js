import {xu} from "xu";
import {Program} from "../../Program.js";

export class hyper extends Program
{
	website   = "http://cd.textfiles.com/phoenix2/01d/hyper25.zip";
	loc       = "dos";
	bin       = "HYPER.EXE";
	args      = r => ["-x", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}

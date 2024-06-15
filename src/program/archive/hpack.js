import {xu} from "xu";
import {Program} from "../../Program.js";

export class hpack extends Program
{
	website   = "https://www.sac.sk/download/pack/hpack79d.zip";
	loc       = "dos";
	bin       = "HPACK79D/HPACK.EXE";
	args      = r => ["X", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}

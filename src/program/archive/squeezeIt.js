import {xu} from "xu";
import {Program} from "../../Program.js";

export class squeezeIt extends Program
{
	website   = "http://cd.textfiles.com/ftp.wwiv.com/pub/GENUTIL/sqz1083.zip";
	loc       = "dos";
	bin       = "SQZ1083/SQZ.EXE";
	args      = r => ["X", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}

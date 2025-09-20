import {xu} from "xu";
import {Program} from "../../Program.js";

export class unesp extends Program
{
	website   = "https://www.sac.sk/download/pack/esp_v192.exe";
	loc       = "dos";
	bin       = "ESP192/UNESP.EXE";
	args      = r => ["x", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}

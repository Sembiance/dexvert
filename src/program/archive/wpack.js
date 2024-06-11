import {xu} from "xu";
import {Program} from "../../Program.js";

export class wpack extends Program
{
	website   = "https://discmaster.textfiles.com/view/227/Gamers%20Arsenal%202%20(Arsenal%20Computer).ISO/faqs/gg2_aug.zip/WSQL.ZIP/WPACK.EXE";
	loc       = "dos";
	bin       = "WPACK.EXE";
	args      = r => [r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}

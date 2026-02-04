import {xu} from "xu";
import {Program} from "../../Program.js";

export class loadram extends Program
{
	website   = "https://discmaster.textfiles.com/view/29622/ibm0040-0049/ibm0047.tar/ibm0047/LEGATOB1.ZIP/LOADRAM.EXE";
	loc       = "dos";
	bin       = "LOADRAM.EXE";
	args      = r => [r.inFile({backslash : true}), r.outDir({backslash : true}), "/C"];
	renameOut = false;
}

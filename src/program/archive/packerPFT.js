import {xu} from "xu";
import {Program} from "../../Program.js";

export class packerPFT extends Program
{
	website   = "http://cd.textfiles.com/psl/pslv3nv08/PRGMMING/DOS/GEN_INST/FINISH30.ZIP";
	loc       = "dos";
	bin       = "FINISH30/PACKER.EXE";
	args      = r => [r.inFile({backslash : true}), "/X"];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}

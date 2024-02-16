import {Program} from "../../Program.js";
import {path} from "std";

export class installIt extends Program
{
	website   = "http://cd.textfiles.com/simtel/simtel0101/simtel/install/ii204.zip";
	unsafe    = true;
	loc       = "dos";
	bin       = "II204/DECOMP.EXE";
	args      = r => [`E:\\${path.basename(r.inFile())}`];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}

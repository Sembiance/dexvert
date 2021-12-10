import {Program} from "../../Program.js";

export class nwunpack extends Program
{
	website   = "https://dosbox-x.com/wiki/Guide%3ASetting-up-networking-in-DOSBox%E2%80%90X";
	loc       = "dos";
	bin       = "NWUNPACK.EXE";
	args      = r => [r.inFile({backslash : true}), r.outDir()];
	renameOut = false;
}

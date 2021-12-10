import {Program} from "../../Program.js";

export class arq extends Program
{
	website   = "https://dosbox-x.com/wiki/Guide%3ASetting-up-networking-in-DOSBox%E2%80%90X";
	loc       = "dos";
	bin       = "ARQ.EXE";
	args      = r => ["-x", r.inFile(), r.outDir()];
	renameOut = false;
}

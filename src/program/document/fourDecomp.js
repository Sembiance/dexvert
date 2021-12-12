import {Program} from "../../Program.js";

export class fourDecomp extends Program
{
	website   = "https://dosbox-x.com/wiki/Guide%3ASetting-up-networking-in-DOSBox%E2%80%90X";
	loc       = "dos";
	bin       = "4DECOMP.EXE";
	args      = async r => [r.inFile({backslash : true}), await r.outFile("OUT.BAT", {backslash : true})];
	renameOut = true;
}

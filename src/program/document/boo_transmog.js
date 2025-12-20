import {Program} from "../../Program.js";

export class boo_transmog extends Program
{
	loc       = "wine";
	bin       = "boo_transmog\\transmog.exe";
	args      = async r => [r.inFile(), await r.outFile("out")];
	renameOut = true;
}

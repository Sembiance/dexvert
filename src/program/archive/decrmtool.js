import {Program} from "../../Program.js";

export class decrmtool extends Program
{
	website   = "http://aminet.net/package/util/pack/decrunchmania-mos";
	package   = "app-arch/decrunchmania";
	bin       = "decrmtool";
	args      = async r => [r.inFile(), await r.outFile("out")];
	renameOut = true;
}

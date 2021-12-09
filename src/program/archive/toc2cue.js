import {Program} from "../../Program.js";

export class toc2cue extends Program
{
	website = "http://cdrdao.sourceforge.net/";
	package = "app-cdr/cdrdao";
	bin     = "toc2cue";
	args    = async r => [r.inFile(), await r.outFile("out.cue")];
}

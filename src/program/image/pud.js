import {Program} from "../../Program.js";

export class pud extends Program
{
	website   = "https://github.com/war2/war2tools/";
	package   = "games-util/war2tools";
	bin       = "pud";
	args      = async r => ["--output", await r.outFile("out.png"), "--png", r.inFile()];
	chain     = "convert[scale:400%]";
	renameOut = true;
}

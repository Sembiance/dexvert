import {Program} from "../../Program.js";

export class kss2wav extends Program
{
	website   = "https://github.com/digital-sound-antiques/libkss";
	package   = "dev-libs/libkss";
	bin       = "kss2wav";
	args      = async r => ["-p120", "-l0", "-n1", "-q1", `-o${await r.outFile("out.wav")}`, r.inFile()];
	renameOut = true;
	chain     = "sox";
}

import {Program} from "../../Program.js";

export class bpgdec extends Program
{
	website = "http://bellard.org/bpg/";
	package = "media-libs/libbpg";
	bin     = "bpgdec";
	args    = async r => ["-o", await r.outFile("out.png"), r.inFile()];
}

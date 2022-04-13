import {Program} from "../../Program.js";

export class pcf2bdf extends Program
{
	website   = "http://www.tsg.ne.jp/GANA/S/pcf2bdf/";
	package   = "media-fonts/pcf2bdf";
	bin       = "pcf2bdf";
	args      = async r => ["-o", await r.outFile("out.bdf"), r.inFile()];
	renameOut = true;
}

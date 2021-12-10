import {Program} from "../../Program.js";

export class amigadepacker extends Program
{
	website = "http://zakalwe.fi/~shd/foss/amigadepacker/";
	package = "app-arch/amigadepacker";
	bin     = "amigadepacker";
	args    = async r => ["-o", await r.outFile("out"), r.inFile()];
}

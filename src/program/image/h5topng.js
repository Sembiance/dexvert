import {Program} from "../../Program.js";

export class h5topng extends Program
{
	website       = "https://github.com/NanoComp/h5utils/";
	gentooPackage = "sci-misc/h5utils";
	bin           = "h5topng";
	args          = async r => ["-o", await r.outFile("out.png"), "-c", "gray", r.inFile()]
}

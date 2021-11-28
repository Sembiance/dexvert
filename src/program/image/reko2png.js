import {Program} from "../../Program.js";

export class reko2png extends Program
{
	website       = "https://github.com/Sembiance/reko2png";
	gentooPackage = "games-util/reko2png";
	gentooOverlay = "dexvert";
	bin           = "reko2png";
	args          = async r => [r.inFile(), await r.outFile("out.png")];
}

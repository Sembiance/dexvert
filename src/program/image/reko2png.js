import {Program} from "../../Program.js";

export class reko2png extends Program
{
	website   = "https://github.com/Sembiance/reko2png";
	package   = "games-util/reko2png";
	bin       = "reko2png";
	args      = async r => [r.inFile(), await r.outFile("out.png")];
	renameOut = true;
}

import {Program} from "../../Program.js";

export class viewCompanion extends Program
{
	website   = "http://www.softwarecompanions.com/viewcomp.html";
	loc       = "win7";
	bin       = "c:\\Program Files\\Software Companions\\ViewCompanion Standard\\viewcompanion.exe";
	args      = r => ["/c", "SVG", r.inFile(), "c:\\out\\outfile.svg"];
	renameOut = true;
	chain     = "deDynamicSVG";
}

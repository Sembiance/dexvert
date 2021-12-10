import {Program} from "../../Program.js";

export class DR2DtoPS extends Program
{
	website   = "https://aminet.net/package/docs/misc/dr2d.lha";
	unsafe    = true;
	loc       = "amigappc";
	bin       = "DR2DtoPS";
	args      = r => [r.inFile(), ">HD:out/outfile.ps"];
	renameOut = true;
	chain     = "inkscape";
}

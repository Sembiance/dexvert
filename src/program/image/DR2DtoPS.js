import {Program} from "../../Program.js";

export class DR2DtoPS extends Program
{
	website    = "https://aminet.net/package/docs/misc/dr2d.lha";
	unsafe     = true;
	bin        = "vamos";
	args       = r => [...Program.vamosArgs("DR2DtoPSDR2DtoPS"), r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.ps")});
	renameOut  = true;
	chain      = "inkscape";
}

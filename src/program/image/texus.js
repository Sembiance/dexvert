import {Program} from "../../Program.js";

export class texus extends Program
{
	website   = "https://discmaster.textfiles.com/view/22850/PCA0498.ISO/Demos/RoboR/_robo.EXE/DATA/TXT/TEXUS.EXE";
	loc       = "wine";
	bin       = "TEXUS.EXE";
	args      = async r => ["-rn", "-mn", "-dn", "-o", await r.outFile("out.tga"), r.inFile()];
	renameOut = true;
	chain     = "dexvert[asFormat:image/tga]";
}

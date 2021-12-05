import {Program} from "../../Program.js";

export class dwg2bmp extends Program
{
	website    = "https://qcad.org/en/";
	package    = "media-gfx/qcad-professional";
	bin        = "dwg2bmp";
	args       = async r => ["-quality=100", `-outfile=${await r.outFile("out.bmp")}`, r.inFile()];
	runOptions = () => ({virtualX : true});
	chain      = "dexvert[asFormat:image/bmp]";
}

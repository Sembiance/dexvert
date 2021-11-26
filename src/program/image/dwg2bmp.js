import {Program} from "../../Program.js";

export class dwg2bmp extends Program
{
	website       = "https://qcad.org/en/";
	gentooPackage = "media-gfx/qcad-professional";
	gentooOverlay = "dexvert";
	bin           = "dwg2bmp";
	args          = async r => ["-quality=100", `-outfile=${await r.outFile("out.bmp")}`, r.inFile()]
	runOptions    = () => ({virtualX : true});
	chain         = "dexvert[asFormat:image/bmp]";
}

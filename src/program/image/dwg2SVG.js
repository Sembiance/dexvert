
import {Program} from "../../Program.js";

export class dwg2SVG extends Program
{
	website       = "https://www.gnu.org/software/libredwg/";
	gentooPackage = "media-gfx/libredwg";
	bin           = "dwg2SVG";
	args          = r => [r.inFile()];
	runOptions    = async r => ({stdoutFilePath : await r.outFile("out.svg")});
	chain         = "deDynamicSVG";
}

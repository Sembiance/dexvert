import {Program} from "../../Program.js";

export class darktable_cli extends Program
{
	website        = "https://www.darktable.org/";
	gentooPackage  = "media-gfx/darktable";
	gentooUseFlags = "cups jpeg2k lua nls openexr openmp webp";
	bin            = "darktable-cli";
	args           = async r => [r.inFile(), await r.outFile("out.png")]
}

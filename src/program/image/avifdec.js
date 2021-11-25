import {Program} from "../../Program.js";

export class avifdec extends Program
{
	website       = "https://github.com/AOMediaCodec/libavif";
	gentooPackage = "media-libs/libavif";
	gentooOverlay = "dexvert";
	bin           = "avifdec";
	args          = async r => [r.inFile(), await r.outFile("out.png")]
}

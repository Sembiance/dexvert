import {Program} from "../../Program.js";

export class avifdec extends Program
{
	website = "https://github.com/AOMediaCodec/libavif";
	package = "media-libs/libavif";
	bin     = "avifdec";
	args    = async r => [r.inFile(), await r.outFile("out.png")];
}

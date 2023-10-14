import {Program} from "../../Program.js";

export class grk_decompress extends Program
{
	website   = "https://github.com/GrokImageCompression/grok";
	package   = "media-libs/grok";
	bin       = "grk_decompress";
	args      = async r => ["-i", r.inFile(), "-o", await r.outFile("out.png")];
	renameOut = true;
}

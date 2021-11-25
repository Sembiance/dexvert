import {Program} from "../../Program.js";

export class cistopbm extends Program
{
	website        = "http://netpbm.sourceforge.net/";
	gentooPackage  = "media-libs/netpbm";
	gentooUseFlags = "X jbig jpeg png postscript rle tiff xml zlib";
	bin            = "cistopbm";
	args           = r => [r.inFile()];
	runOptions     = async r => ({stdoutFilePath : await r.outFile("out.pbm")});
	chain          = "convert";
}

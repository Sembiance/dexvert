import {xu} from "xu";
import {Program} from "../../Program.js";

export class imconv extends Program
{
	website = "ftp://ftp.sdsc.edu/pub/sdsc/graphics/imtools";
	package = "media-gfx/imtools";
	flags   = {
		format    : "Which format to use for conversion. For list run `imformats`"
	};

	bin        = "imconv";
	args       = async r => ["-infile", r.inFile(), ...(r.flags.format ? ["-informat", r.flags.format] : []), "-outformat", "tiff", "-outfile", await r.outFile(`out.tiff`)];
	runOptions = ({timeout : xu.SECOND*20});	// can hang on formats forever (such as gif)
	chain      = "dexvert[asFormat:image/tiff]";
	renameOut  = true;
}

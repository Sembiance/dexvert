import {xu} from "xu";
import {Program} from "../../Program.js";

export class imconv extends Program
{
	website = "ftp://ftp.sdsc.edu/pub/sdsc/graphics/imtools";
	package = "media-gfx/imtools";
	flags   = {
		format    : "Which format to use for conversion. For list run `imformats`",
		outFormat : "Which format to output. Default: tiff"
	};

	bin        = "imconv";
	args       = async r => ["-infile", r.inFile(), ...(r.flags.format ? ["-informat", r.flags.format] : []), "-outformat", r.flags.outFormat || "tiff", "-outfile", await r.outFile(`out.${r.flags.outFormat || "tiff"}`)];
	runOptions = ({timeout : xu.SECOND*20});	// can hang on formats forever (such as gif)
	chain      = r => `dexvert[asFormat:image/${r.flags.outFormat || "tiff"}]`;
	renameOut  = true;
}

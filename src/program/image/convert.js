import {xu} from "xu";
import {Program} from "../../Program.js";

export class convert extends Program
{
	website = "https://www.imagemagick.org/";
	package = "media-gfx/imagemagick";
	flags   = {
		format      : "Specify the input format type, can be useful to ensure ImageMagick only converts the file if it's the correct type. Get list with: magick -list format",	// NOTE: This may bypass id checks by forcing it? So it may not be wise to use everywhere?
		background  : "Specify the background color to use",
		outType     : `Which type to convert to (png || gif || webp || svg). Default: png`,
		scale       : "Scale the image by the given percentage",
		flip        : "Set this to true to flip the image vertically. Default: false",
		removeAlpha : "Set this to true to remove the alpha channel and produce a flat, opaque image. Default: false"
	};

	bin  = "magick";
	args = async r =>
	{
		const a = [];
		if(r.flags.background)
			a.push("-background", r.flags.background);
		
		a.push(`${r.flags.format ? `${r.flags.format}:` : ""}${r.inFile()}`);
		
		// strip all metadata
		a.push("-strip");

		// treat the output filename exactly as given, don't interpret any percent signs that may be in it
		a.push("-define", "filename:literal=true");

		const outType = (r.flags.outType || "png");
		if(outType==="png")
			a.push("-define", "png:exclude-chunks=time");
		if(r.flags.flip)
			a.push("-flip");
		if(r.flags.removeAlpha)
			a.push("-alpha", "off");
		if(r.flags.scale)
			a.push("-scale", r.flags.scale);
		a.push(await r.outFile(`out.${outType}`));
		return a;
	};

	post = r =>
	{
		if(r.stderr.toLowerCase().includes("read error"))
			r.unsafe = true;
	};
	renameOut = true;
	chain     = r => (r.flags.outType==="svg" ? "deDynamicSVG" : null);
}

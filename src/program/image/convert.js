import {Program} from "../../Program.js";

export class convert extends Program
{
	website = "https://www.imagemagick.org/";
	package = "media-gfx/imagemagick";
	flags   = {
		outType     : `Which type to convert to (png || webp || svg). Default: png`,
		flip        : "Set this to true to flip the image vertically. Default: false",
		removeAlpha : "Set this to true to remove the alpha channel and produce a flat, opaque image. Default: false"
	};

	bin  = "convert";
	args = async r =>
	{
		const a = [r.inFile(), "-strip"];
		const outType = (r.flags.outType || "png");
		if(outType==="png")
			a.push("-define", "png:exclude-chunks=time");
		if(r.flags.flip)
			a.push("-flip");
		if(r.flags.removeAlpha)
			a.push("-alpha", "off");
		a.push(await r.outFile(`out.${outType}`));
		return a;
	};

	post = r =>
	{
		if(r.stderr.toLowerCase().includes("read error"))
			r.unsafe = true;
	};
}

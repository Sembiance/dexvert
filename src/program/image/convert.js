import {Program} from "../../Program.js";
import {path} from "std";

export class convert extends Program
{
	website        = "https://www.imagemagick.org/";
	gentooPackage  = "media-gfx/imagemagick";
	gentooUseFlags = "X bzip2 cxx fontconfig fpx heif jbig jpeg jpeg2k lzma openmp png postscript svg tiff truetype webp wmf xml zlib";
	flags          =
	{
		outType     : `Which type to convert to (png || webp || svg). Default: png`,
		flip        : "Set this to true to flip the image vertically. Default: false",
		removeAlpha : "Set this to true to remove the alpha channel and produce a flat, opaque image. Default: false"
	};

	bin  = "convert";
	args = r =>
	{
		const a = [r.inFile(), "-strip"];
		const outType = (r.flags.outType || "png");
		if(outType==="png")
			a.push("-define", "png:exclude-chunks=time");
		if(r.flags.flip)
			a.push("-flip");
		if(r.flags.removeAlpha)
			a.push("-alpha", "off");
		a.push(r.outFile(`out.${outType}`));
		return a;
	}

	post = r =>
	{
		if(r.stderr.toLowerCase().includes("read error"))
			r.unsafe = true;
	}
}

/*

exports.bin = () => "convert";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, `outfile${r.flags.convertExt || ".png"}`)) =>
{
	const convertArgs = [inPath, "-strip", "-define", "png:exclude-chunks=time"];
	if(r.flags.flip)
		convertArgs.push("-flip");
	if(r.flags.removeAlpha)
		convertArgs.push("-alpha", "off");
	convertArgs.push(outPath);
	return convertArgs;
};

exports.post = (state, p, r, cb) =>
{

	return p.util.file.move(path.join(state.output.absolute, `outfile${r.flags.convertExt || ".png"}`), path.join(state.output.absolute, `${state.input.name}${r.flags.convertExt || ".png"}`))(state, p, cb);
};
*/

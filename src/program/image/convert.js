/*
import {Program} from "../../Program.js";

export class convert extends Program
{
	website = "https://www.imagemagick.org/";
	gentooPackage = "media-gfx/imagemagick";
	gentooUseFlags = "X bzip2 cxx fontconfig fpx heif jbig jpeg jpeg2k lzma openmp png postscript svg tiff truetype webp wmf xml zlib";
	flags = {"convertExt":"Which extension to convert to (\".png\", \".webp\", \".svg\"). Default: .png","flip":"Set this to true to flip the image vertically. Default: false","removeAlpha":"Set this to true to remove the alpha channel and produce a flat, opaque image. Default: false"};
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "https://www.imagemagick.org/",
	gentooPackage  : "media-gfx/imagemagick",
	gentooUseFlags : "X bzip2 cxx fontconfig fpx heif jbig jpeg jpeg2k lzma openmp png postscript svg tiff truetype webp wmf xml zlib",
	flags          :
	{
		convertExt  : `Which extension to convert to (".png", ".webp", ".svg"). Default: .png`,
		flip        : "Set this to true to flip the image vertically. Default: false",
		removeAlpha : "Set this to true to remove the alpha channel and produce a flat, opaque image. Default: false"
	}
};

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
	if((r.results || "").toLowerCase().includes("read error"))
		r.untrustworthyConversion = true;

	return p.util.file.move(path.join(state.output.absolute, `outfile${r.flags.convertExt || ".png"}`), path.join(state.output.absolute, `${state.input.name}${r.flags.convertExt || ".png"}`))(state, p, cb);
};
*/

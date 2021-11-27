import {Format} from "../../Format.js";

export class gem extends Format
{
	name       = "GEM Raster Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/GEM_Raster";
	ext        = [".img", ".ximg", ".timg"];
	mimeType   = "image/x-gem";
	magic      = ["GEM bitmap", "GEM HYPERPAINT Image data", "GEM Image data", "Extended GEM bitmap", /^GEM .{4} Image data/];

	// Recoil seems to handle all the files
	// Abydos and nconvert handle the color in flag_b24 and tru256
	// nconvert messes up some other images colorspaces (as usual for nconvert)
	converters = ["recoil2png", `abydosconvert[format:${this.mimeType}]`, "deark", "nconvert"]
}

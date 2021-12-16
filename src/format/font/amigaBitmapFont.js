import {Format} from "../../Format.js";

export class amigaBitmapFont extends Format
{
	name         = "Amiga Bitmap Font";
	website      = "http://fileformats.archiveteam.org/wiki/Amiga_bitmap_font";
	ext          = [".font"];
	magic        = ["Amiga bitmap Font", "AmigaOS bitmap font"];
	trustMagic   = true;
	keepFilename = true;
	auxFiles     = (input, otherFiles, otherDirs) =>
	{
		const otherDir = otherDirs.find(o => o.base.toLowerCase()===input.name.toLowerCase());
		return otherDir ? [otherDir] : false;
	};
	converters = ["Fony"];
}

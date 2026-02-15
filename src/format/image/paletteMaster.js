import {Format} from "../../Format.js";

export class paletteMaster extends Format
{
	name       = "Palette Master";
	website    = "http://fileformats.archiveteam.org/wiki/Palette_Master";
	ext        = [".art"];
	fileSize   = 36864;
	converters = ["recoil2png[format:ART.PaletteMaster]"];
}

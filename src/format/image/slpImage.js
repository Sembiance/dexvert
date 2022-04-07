import {Format} from "../../Format.js";

export class slpImage extends Format
{
	name        = "SLP Image";
	website     = "http://fileformats.archiveteam.org/wiki/Age_of_Empires_Graphics_File";
	ext         = [".slp"];
	magic       = ["SLP Image"];
	unsupported = true;
	notes       = "Could use SLP Editor or SLPCNVT (see sandbox/app) but both had issues opening several files and since it's just for AoE, not worth the effort.";
}

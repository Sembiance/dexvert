import {Format} from "../../Format.js";

export class esm extends Format
{
	name       = "Enhanced Simplex";
	website    = "http://fileformats.archiveteam.org/wiki/Enhanced_Simplex";
	ext        = [".esm"];
	magic      = ["Enhanced Simplex bitmap"];
	converters = ["recoil2png", "nconvert"];
}

import {Format} from "../../Format.js";

export class iim extends Format
{
	name       = "InShape 3D IIM";
	website    = "http://fileformats.archiveteam.org/wiki/InShape_IIM";
	ext        = [".iim"];
	magic      = ["InShape IIM bitmap", "deark: iim", "Inshape :iim:"];
	converters = ["deark[module:iim]", "nconvert[format:iim]", "recoil2png", "wuimg"];
}

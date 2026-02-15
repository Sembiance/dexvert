import {Format} from "../../Format.js";

export class zxp extends Format
{
	name       = "ZX-Paintbrush";
	website    = "http://fileformats.archiveteam.org/wiki/ZX-Paintbrush";
	ext        = [".zxp"];
	magic      = ["ZX-Paintbrush"];
	converters = ["recoil2png[format:ZXP]"];
}

import {Format} from "../../Format.js";

export class rgh extends Format
{
	name       = "ZZ_ROUGH";
	website    = "http://fileformats.archiveteam.org/wiki/ZZ_ROUGH";
	ext        = [".rgh"];
	magic      = ["ZZ ROUGH bitmap", "ZZ Rough :zzrough:"];
	converters = ["recoil2png[format:RGH]", "nconvert[format:zzrough]"];
}

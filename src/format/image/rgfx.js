import {Format} from "../../Format.js";

export class rgfx extends Format
{
	name        = "IFF Retargetable Graphic";
	website     = "http://fileformats.archiveteam.org/wiki/RGFX";
	ext         = [".rgfx", ".rgx"];
	magic       = ["IFF Retargetable Graphics bitmap", "deark: rgfx (IFF-RGFX)"];
	converters  = ["deark[module:rgfx]"];
}

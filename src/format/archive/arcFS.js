import {Format} from "../../Format.js";

export class arcFS extends Format
{
	name       = "ArcFS Archive";
	website    = "http://fileformats.archiveteam.org/wiki/ArcFS";
	ext        = [".arc"];
	magic      = ["RISC OS archive (ArcFS format)", "Acorn ArcFS Archive", "Archive: ArcFS", "deark: arcfs"];
	converters = ["nspark", "deark[module:arcfs]"];
}

import {Format} from "../../Format.js";

export class pakleo extends Format
{
	name       = "PAKLEO Archive";
	website    = "http://fileformats.archiveteam.org/wiki/PAKLEO";
	ext        = [".pll"];
	magic      = ["PAKLEO compressed archive", /^PAKLeo archive data$/, "deark: pakleo (PAKLEO)"];
	converters = ["unpakleo", "deark[module:pakleo]"];
}

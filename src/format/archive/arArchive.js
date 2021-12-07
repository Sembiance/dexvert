import {Format} from "../../Format.js";

export class arArchive extends Format
{
	name       = "AR Archive";
	website    = "http://fileformats.archiveteam.org/wiki/AR";
	ext        = [".a", ".lib"];
	magic      = ["current ar archive", "ar archive"];
	converters = ["deark", "ar"];
}

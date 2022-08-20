import {Format} from "../../Format.js";

export class nuFX extends Format
{
	name       = "NuFX Archive";
	website    = "http://fileformats.archiveteam.org/wiki/NuFX";
	ext        = [".bxy", ".shk"];
	magic      = ["current ar archive", "ar archive"];
	converters = ["nulib2", "acx"];
}

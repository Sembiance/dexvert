import {Format} from "../../Format.js";

export class nuFX extends Format
{
	name       = "NuFX/ShrinkIt Archive";
	website    = "http://fileformats.archiveteam.org/wiki/NuFX";
	ext        = [".bxy", ".shk"];
	magic      = ["NuFile archive", "NuFX archive", /^fmt\/850( |$)/];
	converters = ["nulib2", "acx"];
}

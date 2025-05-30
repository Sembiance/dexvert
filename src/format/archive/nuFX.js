import {Format} from "../../Format.js";

export class nuFX extends Format
{
	name       = "NuFX/ShrinkIt Archive";
	website    = "http://fileformats.archiveteam.org/wiki/NuFX";
	ext        = [".bxy", ".shk"];
	magic      = ["NuFile archive", "NuFX archive", "deark: nufx", /^fmt\/850( |$)/];
	idMeta     = ({proDOSTypeCode, proDOSTypeAux}) => proDOSTypeCode==="LBR" && proDOSTypeAux==="8002";
	converters = ["nulib2", "acx", "deark[module:nufx]"];
}

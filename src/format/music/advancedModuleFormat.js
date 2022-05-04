import {Format} from "../../Format.js";

export class advancedModuleFormat extends Format
{
	name         = "Advanced Module Format Module";
	website      = "http://fileformats.archiveteam.org/wiki/Dual_Module_Player_DSMI";
	ext          = [".amf"];
	magic        = ["Advanced Module Format", "AMF Module", /^fmt\/960( |$)/];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123", "openmpt123"];
}

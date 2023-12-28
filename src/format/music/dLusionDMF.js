import {Format} from "../../Format.js";

export class dLusionDMF extends Format
{
	name         = "D-Lusion Music Format";
	website      = "http://fileformats.archiveteam.org/wiki/D-Lusion_Music_File";
	ext          = [".dmf"];
	magic        = ["Xtracker DMF Module", "D-Lusion Music Format module"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123[matchType:magic]", "openmpt123"];
}

import {Format} from "../../Format.js";

export class dLusionDMF extends Format
{
	name         = "D-Lusion Music Format";
	website      = "http://fileformats.archiveteam.org/wiki/DMF";
	ext          = [".dmf"];
	magic        = ["Xtracker DMF Module", "D-Lusion Music Format module"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "openmpt123"];
}

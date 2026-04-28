import {Format} from "../../Format.js";

export class fmTracker extends Format
{
	name           = "FMTracker Module";
	ext            = [".fmt"];
	forbidExtMatch = true;
	magic          = ["FMTracker module"];
	metaProvider   = ["musicInfo"];
	converters     = ["openmpt123"];
}

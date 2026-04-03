import {Format} from "../../Format.js";

export class stoneTrackerSample extends Format
{
	name           = "StoneTracker Sample";
	ext            = [".sps"];
	forbidExtMatch = true;
	magic          = ["StoneTracker Samples"];
	converters     = ["vibe2wav"];
}

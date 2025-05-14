import {Format} from "../../Format.js";

export class futureVisionFSTVideo extends Format
{
	name       = "FutureVision FST video";
	website    = "https://wiki.multimedia.cx/index.php/FutureVision_FST";
	ext        = [".fst"];
	magic      = ["FutureVision FST video"];
	converters = ["na_game_tool[format:fst]"];
}

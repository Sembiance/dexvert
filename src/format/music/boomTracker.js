import {Format} from "../../Format.js";

export class boomTracker extends Format
{
	name         = "Boom Tracker";
	ext          = [".cff"];
	magic        = ["BoomTracker", "CFF Song"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}

import {Format} from "../../Format.js";

export class stoneTracker extends Format
{
	name        = "StoneTracker Module";
	ext         = [".spm", ".sps"];
	matchPreExt = true;
	magic       = ["StoneTracker Module"];
	unsupported = true;
}


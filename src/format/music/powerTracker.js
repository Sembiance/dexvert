import {Format} from "../../Format.js";

export class powerTracker extends Format
{
	name         = "PowerTracker Module";
	ext          = [".pt"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}

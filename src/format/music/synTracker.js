import {Format} from "../../Format.js";

export class synTracker extends Format
{
	name         = "SynTracker Module";
	ext          = [".synmod", ".st"];
	magic        = ["SynTracker module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}

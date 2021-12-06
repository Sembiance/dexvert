import {Format} from "../../Format.js";

export class deliTrackerCustom extends Format
{
	name         = "Delitracker Customplay Module";
	ext          = [".cus"];
	magic        = ["Delitracker Customplay Module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}

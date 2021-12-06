import {Format} from "../../Format.js";

export class medleySound extends Format
{
	name         = "MedleySound Module";
	ext          = [".mso"];
	magic        = ["MedlySound module"];	// trid appears to misspell this
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}

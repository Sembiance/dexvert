import {Format} from "../../Format.js";

export class medleySound extends Format
{
	name         = "MedleySound Module";
	ext          = [".mso"];
	magic        = ["MedleySound module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}

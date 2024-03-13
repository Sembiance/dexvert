import {Format} from "../../Format.js";

export class anders0land extends Format
{
	name         = "Anders 0land Module";
	ext          = [".hot"];
	magic        = ["Anders 0land music", "Anders Oland music"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}

import {Format} from "../../Format.js";

export class mikeDavies extends Format
{
	name         = "Mike Davies Module";
	ext          = [".md"];
	magic        = ["Mike Davies module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}

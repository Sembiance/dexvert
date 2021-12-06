import {Format} from "../../Format.js";

export class synthesis extends Format
{
	name         = "Synthesis Module";
	ext          = [".syn"];
	magic        = [/^Synthesis [Mm]odule/];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}

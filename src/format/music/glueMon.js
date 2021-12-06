import {Format} from "../../Format.js";

export class glueMon extends Format
{
	name         = "GlueMon Module";
	ext          = [".glue"];
	magic        = ["GlueMon module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}

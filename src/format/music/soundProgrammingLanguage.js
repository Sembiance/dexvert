import {Format} from "../../Format.js";

export class soundProgrammingLanguage extends Format
{
	name         = "Sound Programming Language Module";
	ext          = [".spl"];
	magic        = ["SOPROL Sound Programming Language module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}

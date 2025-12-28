import {Format} from "../../Format.js";

export class mozlz4 extends Format
{
	name           = "MOZLZ4 Compressed";
	ext            = [".mozlz4", ".jsonlz4"];
	magic          = ["Mozilla mozLz4 compressed data", "Mozilla search engines info", /^Mozilla lz4 compressed data/];
	packed         = true;
	converters     = ["mozlz4"];
}

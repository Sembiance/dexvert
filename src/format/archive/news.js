import {Format} from "../../Format.js";

export class news extends Format
{
	name       = "Newsgroup Content";
	magic      = ["saved news", /^(old )?news(, ASCII|ISO-8859 )?( text)?/, /^batched news text/];
	converters = ["unnews"];
	notes      = "Converter currently doesn't handle when just a single newsgroup message is saved in a file";
}

import {Format} from "../../Format.js";

export class davidHanneyChiptune extends Format
{
	name         = "David Hanney Chiptune";
	ext          = [".dh"];
	magic        = ["David Hanney chiptune"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}

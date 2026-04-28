import {Format} from "../../Format.js";

export class magicLanternDIFF extends Format
{
	name           = "Magic Lantern DIFF Animation";
	ext            = [".diff"];
	forbidExtMatch = true;
	magic          = ["Magic Lantern DIFF animation"];
	converters     = ["vibe2avi"];
}

import {Format} from "../../Format.js";

export class homeWorld2ROTGraphics extends Format
{
	name           = "HomeWorld 2 ROT Graphics";
	ext            = [".rot"];
	forbidExtMatch = true;
	magic          = ["HomeWorld 2 ROT Graphics", "Home World 2 - ROT graphics"];
	converters     = ["wuimg"];	// currently only supports uncompressed versions, of which I haven't found any samples of yet
}

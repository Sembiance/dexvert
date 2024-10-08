import {xu} from "xu";
import {Format} from "../../Format.js";

export class avfVideo extends Format
{
	name           = "AVF Video";
	website        = "https://wiki.multimedia.cx/index.php/AVF";
	ext            = [".avf"];
	forbidExtMatch = true;
	magic          = [/^AVF video$/, "AVF Video (old)"];
	weakMagic      = ["AVF Video (old)"];
	converters     = ["na_game_tool[format:avf]"];
}

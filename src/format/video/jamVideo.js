import {xu} from "xu";
import {Format} from "../../Format.js";

export class jamVideo extends Format
{
	name           = "JAM Video";
	website        = "https://wiki.multimedia.cx/index.php/JAM";
	ext            = [".jam"];
	forbidExtMatch = true;
	magic          = ["JAM Video", "JAM game video"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:jam]"];
}

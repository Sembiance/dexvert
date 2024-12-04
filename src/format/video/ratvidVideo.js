import {xu} from "xu";
import {Format} from "../../Format.js";

export class ratvidVideo extends Format
{
	name           = "RATVID/VIDPAK Video";
	website        = "https://wiki.multimedia.cx/index.php/VIDPAK";
	ext            = [".vdo"];
	forbidExtMatch = true;
	magic          = ["RATVID video", "VIDPAK / RATVID video"];
	converters     = ["na_game_tool[format:ratvid]"];
}

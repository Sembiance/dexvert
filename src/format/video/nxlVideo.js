import {xu} from "xu";
import {Format} from "../../Format.js";

export class nxlVideo extends Format
{
	name           = "NXL Video";
	website        = "https://wiki.multimedia.cx/index.php/NXL";
	ext            = [".nxl"];
	forbidExtMatch = true;
	magic          = ["NXL Video", "NXL2 video"];
	converters     = ["na_game_tool[format:nxl]"];
}

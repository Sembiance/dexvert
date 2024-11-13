import {Format} from "../../Format.js";

export class vdoVideo extends Format
{
	name           = "Harro Media VDO video";
	website        = "https://wiki.multimedia.cx/index.php/Harrow_Media_VDO";
	ext            = [".vdo", ".vd"];
	forbidExtMatch = true;
	magic          = ["VDO video"];
	converters     = ["na_game_tool[format:vdo]"];
}

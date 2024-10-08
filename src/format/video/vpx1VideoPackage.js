import {xu} from "xu";
import {Format} from "../../Format.js";

export class vpx1VideoPackage extends Format
{
	name           = "VPX1 Video Package";
	website        = "https://wiki.multimedia.cx/index.php/VPX1";
	ext            = [".vpx"];
	forbidExtMatch = true;
	magic          = ["VPX1 Video Package"];
	converters     = ["na_game_tool[format:vpx1]"];
}

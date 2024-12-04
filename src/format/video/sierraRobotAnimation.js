import {xu} from "xu";
import {Format} from "../../Format.js";

export class sierraRobotAnimation extends Format
{
	name           = "Sierra Robot Animation";
	website        = "https://wiki.multimedia.cx/index.php/Robot_Animation";
	ext            = [".rbt"];
	forbidExtMatch = true;
	magic          = ["Sierra Robot Animation"];
	converters     = ["na_game_tool[format:rbt]"];
}

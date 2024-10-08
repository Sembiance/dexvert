import {xu} from "xu";
import {Format} from "../../Format.js";

export class tviVideo extends Format
{
	name       = "Terminal Reality TVI Video";
	website    = "https://wiki.multimedia.cx/index.php/TVI";
	ext        = [".tvi"];
	converters = ["na_game_tool[format:tvi]"];
}

import {Format} from "../../Format.js";

export class arkOfTimeAN extends Format
{
	name       = "Ark of Time AN Video";
	website    = "https://wiki.multimedia.cx/index.php/Ark_of_Time_AN";
	ext        = [".an"];
	byteCheck  = [{offset : 2, match : [0x00, 0x00, 0x12]}];
	converters = ["na_game_tool[format:ark-an]"];
}

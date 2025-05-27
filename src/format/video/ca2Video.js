import {Format} from "../../Format.js";

export class ca2Video extends Format
{
	name       = "CA2 Video";
	website    = "https://wiki.multimedia.cx/index.php/CA2";
	ext        = [".ca2"];
	byteCheck  = [{offset : 0, match : [0x80, 0x00, 0x00, 0x00]}];
	converters = ["na_game_tool[format:ca2]"];
}

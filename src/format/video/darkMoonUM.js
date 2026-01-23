import {Format} from "../../Format.js";

export class darkMoonUM extends Format
{
	name       = "Dark Moon UM Video";
	ext        = [".um"];
	idCheck    = inputFile => inputFile.size>=33536 && inputFile.size%33536===0;
	converters = ["na_game_tool[format:um]"];
}

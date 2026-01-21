import {Format} from "../../Format.js";

export class ninellGraphic extends Format
{
	name       = "Ninell Graphic";
	magic      = ["Ninell Graphic"];
	converters = ["na_game_tool[format:naf][outType:png]"];
}

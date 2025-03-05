import {Format} from "../../Format.js";

export class yoMatiasMXV extends Format
{
	name       = "Yo-Matias MXV";
	ext        = [".mxv"];
	magic      = ["Caiman Video data"];
	converters = ["na_game_tool[format:yo-mxv]"];
}

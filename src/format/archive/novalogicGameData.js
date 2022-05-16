import {Format} from "../../Format.js";

export class novalogicGameData extends Format
{
	name       = "Novalogic Game Data Archive";
	ext        = [".pff"];
	magic      = ["Novalogic game data archive"];
	converters = ["gameextractor"];
}

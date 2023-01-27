import {Format} from "../../Format.js";

export class apogeeIMF extends Format
{
	name         = "Apogee IMF";
	ext          = [".imf"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay", "gamemus"];
}

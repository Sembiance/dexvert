import {Format} from "../../Format.js";

export class martinFernandez extends Format
{
	name         = "Martin Fernandez AdLib Module";
	ext          = [".adlib"];
	magic        = ["Martin Fernandez Ad Lib module"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}

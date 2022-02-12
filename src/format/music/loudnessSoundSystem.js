import {Format} from "../../Format.js";

export class loudnessSoundSystem extends Format
{
	name         = "Loudness Sound System";
	ext          = [".lds"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}

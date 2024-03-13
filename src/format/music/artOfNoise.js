import {Format} from "../../Format.js";

export class artOfNoise extends Format
{
	name         = "Art of Noise Module";
	website      = "http://fileformats.archiveteam.org/wiki/Art_of_Noise_module";
	ext          = [".aon"];
	magic        = ["Art Of Noise Module sound file", /^Art Of Noise \d-channel module$/, "Art of Noise Tracker Song", /^fmt\/(1623|1624)( |$)/];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}

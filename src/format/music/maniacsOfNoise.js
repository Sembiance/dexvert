import {Format} from "../../Format.js";

export class maniacsOfNoise extends Format
{
	name         = "Maniacs of Noise Module";
	website      = "http://fileformats.archiveteam.org/wiki/Maniacs_of_Noise";
	ext          = [".mon"];
	magic        = ["M.O.N New module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}

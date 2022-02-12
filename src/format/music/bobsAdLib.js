import {Format} from "../../Format.js";

export class bobsAdLib extends Format
{
	name         = "Bob's AdLib";
	website      = "http://fileformats.archiveteam.org/wiki/Bob%27s_Adlib_Music";
	ext          = [".bam"];
	magic        = ["Bob's AdLib Music module"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}

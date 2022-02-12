import {Format} from "../../Format.js";

export class bobsAdLib extends Format
{
	name         = "Bob's AdLib";
	ext          = [".bam"];
	magic        = ["Bob's AdLib Music module"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}

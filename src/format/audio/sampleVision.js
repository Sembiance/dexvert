import {Format} from "../../Format.js";

export class sampleVision extends Format
{
	name         = "Turtle Beach Sample Vision Audio";
	website      = "http://fileformats.archiveteam.org/wiki/Sample_Vision";
	ext          = [".smp"];
	magic        = ["Sample Vision file", "Turtle Beach Sample Vision audio sample", /^fmt\/1560( |$)/];
	metaProvider = ["soxi"];
	converters   = ["sox"];
}

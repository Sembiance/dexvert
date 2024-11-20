import {Format} from "../../Format.js";

export class epocSketch extends Format
{
	name       = "EPOC/Psion Sketch";
	website    = "http://fileformats.archiveteam.org/wiki/EPOC_Sketch";
	magic      = ["EPOC/Psion Sketch bitmap", /^Psion Series 5 Sketch image/];
	converters = ["deark[module:epocimage]", "konvertor"];
}

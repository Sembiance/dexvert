import {Format} from "../../Format.js";

export class epocSketch extends Format
{
	name       = "EPOC/Psion Sketch";
	website    = "http://fileformats.archiveteam.org/wiki/EPOC_Sketch";
	magic      = ["EPOC/Psion Sketch bitmap", /^Psion Series 5 Sketch image/, /^Psion Series 5 Record file Sketch image/, "deark: epocimage (EPOC Sketch)"];
	converters = ["deark[module:epocimage]", "konvertor"];
}

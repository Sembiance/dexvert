import {Format} from "../../Format.js";

export class graph2Font extends Format
{
	name       = "Graph2Font";
	website    = "http://fileformats.archiveteam.org/wiki/Graph2Font";
	ext        = [".g2f", ".mch"];
	magic      = ["Graph2Font bitmap"];
	fileSize   = {".mch" : [30833, 32993]};
	converters = ["recoil2png[format:MCH,G2F]"];
}

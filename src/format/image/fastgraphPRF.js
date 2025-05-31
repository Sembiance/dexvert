import {Format} from "../../Format.js";

export class fastgraphPRF extends Format
{
	name       = "Fastgraph Pixel Run Format";
	website    = "http://fileformats.archiveteam.org/wiki/Fastgraph_Pixel_Run_Format";
	ext        = [".prf", ".spr", ".ppr"];
	magic      = ["Fastgraph Pixel Run Format bitmap", "deark: fastgraph_spr"];
	converters = ["deark[module:fastgraph_spr]"];
}

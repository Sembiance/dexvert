import {Format} from "../../Format.js";

export class shg extends Format
{
	name       = "Segmented Hypergraphics Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/Segmented_Hypergraphics";
	ext        = [".shg"];
	magic      = ["Segmented Hypergraphics bitmap", "deark: shg (MRB)"];
	converters = ["deark[module:shg]"];
}

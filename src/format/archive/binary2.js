import {Format} from "../../Format.js";

export class binary2 extends Format
{
	name       = "Binary ][ Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Binary_II";
	ext        = [".bny", ".bqy"];
	magic      = ["Binary ][ archive", "Binary II (apple ][) data", "deark: binary_ii"];
	converters = ["nulib2", "deark[module:binary_ii]"];
}

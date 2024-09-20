import {Format} from "../../Format.js";

export class hdf5 extends Format
{
	name       = "Hierarchical Data Format v5";
	website    = "http://fileformats.archiveteam.org/wiki/HDF";
	ext        = [".h5"];
	mimeType   = "application/x-hdf";
	magic      = ["Hierarchical Data Format (version 5)", "Hierarchical Data Format 5", "application/x-hdf", /^NCSA Hierarchical Data Format 5$/, /^fmt\/807( |$)/];
	notes      = "Only support converting to grayscale.";
	converters = ["h5topng"];
}

import {Format} from "../../Format.js";

export class hdf4 extends Format
{
	name       = "Hierarchical Data Format v4";
	website    = "http://fileformats.archiveteam.org/wiki/HDF";
	ext        = [".hdf"];
	mimeType   = "application/x-hdf";
	magic      = ["Hierarchical Data Format (version 4)", "application/x-hdf", /^NCSA Hierarchical Data Format$/, /^fmt\/1041( |$)/];
	notes      = "nconvert doesn't seem to handle all files, such as input_256 and input_truecolor";
	converters = ["nconvert"];
}

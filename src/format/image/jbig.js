import {Format} from "../../Format.js";

export class jbig extends Format
{
	name         = "Joint Bi-Level Image experts Group";
	website      = "http://fileformats.archiveteam.org/wiki/JBIG";
	ext          = [".jbg", ".jbig", ".bie"];
	magic        = ["JBIG raster bitmap"];
	notes        = "Sample file mx.jbg converts to garbage, not sure why.";
	metaProvider = ["image"];
	converters   = ["convert", "wuimg"];
}

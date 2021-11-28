import {Format} from "../../Format.js";

export class rla extends Format
{
	name         = "Alias Wavefront RLA";
	website      = "http://fileformats.archiveteam.org/wiki/RLA";
	ext          = [".rla"];
	magic        = ["Alias Wavefront Raster bitmap"];
	metaProvider = ["image"];
	converters   = ["convert", "nconvert"];
}

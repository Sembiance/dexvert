import {Format} from "../../Format.js";

export class rla extends Format
{
	name         = "Alias Wavefront RLA";
	website      = "http://fileformats.archiveteam.org/wiki/RLA";
	ext          = [".rla"];
	magic        = ["Alias Wavefront Raster bitmap"];
	metaProvider = ["image"];
	converters   = ["imconv[format:rla]", "convert", "nconvert"];	// iconvert also supports this but often just outputs a grey image
}

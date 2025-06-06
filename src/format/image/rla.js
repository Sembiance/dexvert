import {Format} from "../../Format.js";

export class rla extends Format
{
	name         = "Alias Wavefront RLA";
	website      = "http://fileformats.archiveteam.org/wiki/RLA";
	ext          = [".rla"];
	magic        = ["Alias Wavefront Raster bitmap", "Wavefront Raster Image :rla:"];
	metaProvider = ["image"];
	converters   = ["imconv[format:rla]", "convert", "nconvert[format:rla]"];	// iconvert also supports this but often just outputs a grey image
}

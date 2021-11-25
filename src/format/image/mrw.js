import {Format} from "../../Format.js";

export class mrw extends Format
{
	name          = "Minolta RAW";
	website       = "http://fileformats.archiveteam.org/wiki/Minolta";
	ext           = [".mrw"];
	magic         = ["Minolta RAW", "Minolta Dimage camera raw", "Minolta Dimage RAW image"];
	mimeType      = "image/x-minolta-mrw";
	converters    = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"]
	metaProviders = ["image", "darkTable"];
}

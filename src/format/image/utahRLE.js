import {Format} from "../../Format.js";

export class utahRLE extends Format
{
	name         = "Utah RLE";
	website      = "http://fileformats.archiveteam.org/wiki/Utah_RLE";
	ext          = [".rle"];
	magic        = ["Utah Raster Toolkit bitmap", "RLE image data"];
	metaProvider = ["image"];
	converters   = ["convert", "recoil2png"];
}

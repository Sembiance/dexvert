import {Format} from "../../Format.js";

export class utahRLE extends Format
{
	name         = "Utah RLE";
	website      = "http://fileformats.archiveteam.org/wiki/Utah_RLE";
	ext          = [".rle"];
	magic        = ["Utah Raster Toolkit bitmap", "RLE image data", "Utah Raster :rle:"];
	metaProvider = ["image"];
	converters   = ["nconvert[format:rle]", "recoil2png", "imconv[format:rle][matchType:magic]", "wuimg[matchType:magic]", "convert"];	// convert sometimes produces just a black square, see mandrill.rle
	verify       = ({meta}) => meta.colorCount>1;
}

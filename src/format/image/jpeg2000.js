import {Format} from "../../Format.js";

export class jpeg2000 extends Format
{
	name         = "JPEG 2000";
	website      = "http://fileformats.archiveteam.org/wiki/JPEG_2000";
	ext          = [".jp2"];
	mimeType     = "image/jp2";
	magic        = ["JPEG 2000", "JP2 (JPEG 2000"];
	metaProvider = ["image"];
	converters   = ["convert", "gimp"];
}

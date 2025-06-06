import {Format} from "../../Format.js";

export class otaBitmap extends Format
{
	name         = "Nokia Over the Air Bitmap";
	website      = "http://fileformats.archiveteam.org/wiki/OTA_bitmap";
	ext          = [".otb"];
	magic        = ["Nokia OTA bitmap :otb:"];
	metaProvider = ["image"];
	converters   = ["convert", "wuimg"];	// nconvert fails to convert properly the 1 sample we have
}

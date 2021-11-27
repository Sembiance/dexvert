import {Format} from "../../Format.js";

export class otaBitmap extends Format
{
	name          = "Nokia Over the Air Bitmap";
	website       = "http://fileformats.archiveteam.org/wiki/OTA_bitmap";
	ext           = [".otb"];
	converters    = ["convert"]
	metaProviders = ["image"];
}

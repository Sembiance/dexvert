import {Format} from "../../Format.js";

export class jpegXR extends Format
{
	name       = "JPEG XR";
	website    = "http://fileformats.archiveteam.org/wiki/JPEG_XR";
	ext        = [".jxr", ".hdp", ".wdp", ".wmp"];
	mimeType   = "image/vnd.ms-photo";
	magic      = ["JPEG XR bitmap", "JPEG Extended Range", "JPEG-XR Image"];
	converters = ["nconvert"];
}

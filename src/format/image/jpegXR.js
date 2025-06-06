import {Format} from "../../Format.js";

export class jpegXR extends Format
{
	name       = "JPEG XR";
	website    = "http://fileformats.archiveteam.org/wiki/JPEG_XR";
	ext        = [".jxr", ".hdp", ".wdp", ".wmp"];
	mimeType   = "image/vnd.ms-photo";
	magic      = ["JPEG XR bitmap", "JPEG Extended Range", "JPEG-XR Image", "image/jxr", "deark: tiff (JPEG XR)", "JPEG XR :jxr:", /^fmt\/590( |$)/];
	converters = ["nconvert[format:jxr]"];
}

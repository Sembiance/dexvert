import {Format} from "../../Format.js";

export class xvThumbnail extends Format
{
	name       = "XV Thumbnail";
	website    = "http://fileformats.archiveteam.org/wiki/XV_thumbnail";
	magic      = ["XV thumbnail image data", "Xv's Visual Schnauzer bitmap", /^fmt\/1497( |$)/];
	converters = ["wuimg", "nconvert", "uniconvertor[outType:png]"];	// only wuimg seems to support color thumbs
}

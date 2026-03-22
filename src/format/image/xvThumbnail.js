import {Format} from "../../Format.js";

export class xvThumbnail extends Format
{
	name       = "XV Thumbnail";
	website    = "http://fileformats.archiveteam.org/wiki/XV_thumbnail";
	mimeType   = "image/x-xv-thumbnail";
	magic      = ["XV thumbnail image data", "Xv's Visual Schnauzer bitmap", "XV visual schnauzer", /^fmt\/1497( |$)/];
	converters = ["wuimg[format:pnm]", `abydosconvert[format:${this.mimeType}]`, "nconvert", "uniconvertor[outType:png]"];	// only wuimg and abydosconvert seem to support color thumbs
}

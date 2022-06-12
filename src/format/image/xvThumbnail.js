import {Format} from "../../Format.js";

export class xvThumbnail extends Format
{
	name       = "XV Thumbnail";
	magic      = ["XV thumbnail image data", "Xv's Visual Schnauzer bitmap", /^fmt\/1497( |$)/];
	converters = ["nconvert", "uniconvertor[outType:png]"];
}

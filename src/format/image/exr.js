import {Format} from "../../Format.js";

export class exr extends Format
{
	name       = "OpenEXR";
	website    = "http://fileformats.archiveteam.org/wiki/OpenEXR";
	ext        = [".exr"];
	mimeType   = "image/x-exr";
	magic      = ["OpenEXR High Dynamic-Range bitmap", "OpenEXR image data", /^fmt\/1001( |$)/];
	converters = [`abydosconvert[format:${this.mimeType}]`, "iconvert", "gimp"];
}

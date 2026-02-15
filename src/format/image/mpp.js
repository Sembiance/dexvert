import {Format} from "../../Format.js";

export class mpp extends Format
{
	name       = "Multi Palette Picture";
	website    = "http://fileformats.archiveteam.org/wiki/Multi_Palette_Picture";
	ext        = [".mpp"];
	mimeType   = "image/x-multi-palette-picture";
	magic      = ["Multi Palette Picture bitmap", /^fmt\/1471( |$)/];
	converters = ["recoil2png[format:MPP]", `abydosconvert[format:${this.mimeType}]`];
}

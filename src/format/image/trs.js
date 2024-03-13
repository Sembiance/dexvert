import {Format} from "../../Format.js";

export class trs extends Format
{
	name       = "True Colour Sprites";
	website    = "http://fileformats.archiveteam.org/wiki/Spooky_Sprites";
	ext        = [".trs"];
	magic      = ["True Colour Sprites bitmap", /^fmt\/1605( |$)/];
	mimeType   = "image/x-spooky-sprites";
	converters = [`abydosconvert[format:${this.mimeType}]`];
}

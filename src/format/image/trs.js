import {Format} from "../../Format.js";

export class trs extends Format
{
	name       = "True Colour Sprites";
	website    = "http://fileformats.archiveteam.org/wiki/Spooky_Sprites";
	ext        = [".trs"];
	magic      = ["True Colour Sprites bitmap", /^fmt\/1605( |$)/];
	converters = ["wuimg[format:trs]"];	// we don't use abydosconvert with mimeType "image/x-spooky-sprites" because wuimg handles them all and doesn't stretch them
}

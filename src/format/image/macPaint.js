import {Format} from "../../Format.js";

export class macPaint extends Format
{
	name           = "MacPaint Image";
	website        = "http://fileformats.archiveteam.org/wiki/MacPaint";
	ext            = [".mac", ".pntg", ".pic"];
	magic          = ["MacPaint image data"];
	mimeType       = "image/x-macpaint";
	forbiddenMagic = ["Installer VISE Mac package"];
	metaProvider   = ["image"];
	converters     = ["deark", `abydosconvert[format:${this.mimeType}]`, "convert"];
}

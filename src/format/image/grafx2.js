import {Format} from "../../Format.js";

export class grafx2 extends Format
{
	name       = "GrafX2";
	website    = "http://grafx2.chez.com/";
	ext        = [".pkm"];
	magic      = ["GrafX2 bitmap"];
	mimeType   = "image/x-pkm";
	converters = [`abydosconvert[format:${this.mimeType}]`];
}

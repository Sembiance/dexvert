import {Format} from "../../Format.js";

export class theDraw extends Format
{
	name           = "TheDraw File";
	website        = "http://fileformats.archiveteam.org/wiki/TheDraw_Save_File";
	ext            = [".td"];
	forbidExtMatch = true;
	mimeType       = "image/x-thedraw";
	magic          = ["TheDraw design"];
	converters     = [`abydosconvert[format:${this.mimeType}]`];
}

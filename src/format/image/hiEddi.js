import {Format} from "../../Format.js";

export class hiEddi extends Format
{
	name          = "Hi-Eddi";
	website       = "http://fileformats.archiveteam.org/wiki/Hi-Eddi";
	ext           = [".hed"];
	mimeType      = "image/x-hi-eddi";
	fileSize      = 9218;
	matchFileSize = true;
	converters    = ["nconvert", `abydosconvert[format:${this.mimeType}]`, "view64"];
}

import {Format} from "../../Format.js";
import {_PNG_MAGIC} from "./png.js";
import {_JPG_MAGIC} from "./jpg.js";

export class hiEddi extends Format
{
	name           = "Hi-Eddi";
	website        = "http://fileformats.archiveteam.org/wiki/Hi-Eddi";
	ext            = [".hed"];
	mimeType       = "image/x-hi-eddi";
	fileSize       = 9218;
	matchFileSize  = true;
	forbiddenMagic = [..._PNG_MAGIC, ..._JPG_MAGIC];
	converters     = ["nconvert", `abydosconvert[format:${this.mimeType}]`, "view64"];
}

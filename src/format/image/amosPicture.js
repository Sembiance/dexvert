import {Format} from "../../Format.js";

export class amosPicture extends Format
{
	name       = "AMOS Picture Bank";
	website    = "http://fileformats.archiveteam.org/wiki/AMOS_Picture_Bank";
	ext        = [".abk"];
	mimeType   = "application/x-amos-memorybank";
	magic      = ["AMOS Picture Bank"];
	converters = ["deark[module:abk]", `abydosconvert[format:${this.mimeType}]`, "dumpamos"];
}

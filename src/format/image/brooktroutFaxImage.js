import {Format} from "../../Format.js";

export class brooktroutFaxImage extends Format
{
	name       = "Brooktrout Fax Image";
	website    = "http://fileformats.archiveteam.org/wiki/Brooktrout";
	ext        = [".301"];
	magic      = ["Brooktrout 301 :brk:", /^Brooktrout 301 fax image/];
	converters = ["nconvert[format:brk]"];
}

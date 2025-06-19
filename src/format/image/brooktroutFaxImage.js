import {Format} from "../../Format.js";

export class brooktroutFaxImage extends Format
{
	name       = "Brooktrout Fax Image";
	ext        = [".301"];
	magic      = ["Brooktrout 301 :brk:", /^Brooktrout 301 fax image/];
	converters = ["nconvert[format:brk]"];
}

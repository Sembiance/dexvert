import {Format} from "../../Format.js";

export class labEye extends Format
{
	name       = "LabEye";
	ext        = [".im"];
	mimeType   = "image/x-labeye-image";
	magic      = ["LabEye Image bitmap"];
	converters = [`abydosconvert[format:${this.mimeType}]`];
}

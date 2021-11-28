import {Format} from "../../Format.js";

export class regis extends Format
{
	name       = "ReGIS";
	ext        = [".regis"];
	mimeType   = "image/x-regis";
	converters = [`abydosconvert[format:${this.mimeType}]`];
}

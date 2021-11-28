import {Format} from "../../Format.js";

export class softelText extends Format
{
	name       = "Softel Teletext";
	ext        = [".ep1"];
	mimeType   = "text/x-softel-teletext";
	converters = [`abydosconvert[format:${this.mimeType}]`];
}

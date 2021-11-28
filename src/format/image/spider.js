import {Format} from "../../Format.js";

export class spider extends Format
{
	name       = "SPIDER";
	ext        = [".spi", ".spider"];
	mimeType   = "image/x-spider";
	converters = [`abydosconvert[format:${this.mimeType}]`];
}

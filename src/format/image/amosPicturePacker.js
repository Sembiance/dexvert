import {Format} from "../../Format.js";

export class amosPicturePacker extends Format
{
	name       = "AMOS Picture Packer";
	ext        = [".bin"];
	mimeType   = "image/x-amos-picturepacker";
	priority   = this.PRIORITY.LOW;
	converters = [`abydosconvert[format:${this.mimeType}]`];
}

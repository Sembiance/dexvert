import {Format} from "../../Format.js";

export class dataShowScreen extends Format
{
	name       = "DataShow Screen";
	ext        = [".scr"];
	mimeType   = "image/x-datashow-screen";
	priority   = this.PRIORITY.LOWEST;
	byteCheck  = [{offset : 2, match : [0x01, 0x01, 0x19, 0x50]}];	// Not confident this is always there, but is for all samples
	converters = [`abydosconvert[format:${this.mimeType}]`];
}

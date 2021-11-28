import {Format} from "../../Format.js";

export class dataShowGraphic extends Format
{
	name       = "DataShow Graphic";
	ext        = [".gra"];
	mimeType   = "image/x-datashow-graphic";
	fileSize   = 64006;	// Can't guarantee it's always this, but the two sample files are this size
	converters = [`abydosconvert[format:${this.mimeType}]`];
}

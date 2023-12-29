import {Format} from "../../Format.js";

export class dataShowGraphic extends Format
{
	name       = "DataShow Graphic";
	website    = "http://fileformats.archiveteam.org/wiki/DataShow_GRA";
	ext        = [".gra"];
	mimeType   = "image/x-datashow-graphic";
	fileSize   = [16006, 64006, 112_012, 153_618, 240_024, 256_024, 307_230, 393_258, 480_048, 786_510];
	converters = [`abydosconvert[format:${this.mimeType}]`];
}

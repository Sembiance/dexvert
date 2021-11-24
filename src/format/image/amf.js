import {Format} from "../../Format.js";

export class amf extends Format
{
	name           = "Amiga Metafile Vector Image";
	website        = "http://fileformats.archiveteam.org/wiki/Amiga_Metafile";
	ext            = [".amf"];
	forbidExtMatch = true;
	magic          = ["IFF data, AMFF AmigaMetaFile format"];
	mimeType       = "image/x-amff";
	converters     = [`abydosconvert[format:${this.mimeType}]`]
}

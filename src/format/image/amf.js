import {Format} from "../../Format.js";

export class amf extends Format
{
	name           = "Amiga Metafile Vector Image";
	website        = "http://fileformats.archiveteam.org/wiki/Amiga_Metafile";
	ext            = [".amf"];
	forbidExtMatch = true;
	mimeType       = "image/x-amff";
	magic          = ["IFF data, AMFF AmigaMetaFile format"];
	converters     = [`abydosconvert[format:${this.mimeType}]`];
}

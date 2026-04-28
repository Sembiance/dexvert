import {Format} from "../../Format.js";

export class painterRIF extends Format
{
	name           = "Painter Raster Image Format";
	website        = "http://fileformats.archiveteam.org/wiki/Painter_RIFF";
	ext            = [".rif"];
	forbidExtMatch = true;
	magic          = ["Painter Raster Image Format bitmap", "Painter Classic RIFF", /^x-fmt\/187( |$)/];
	weakMagic      = ["Painter Classic RIFF"];
	converters     = ["painterClassic"];
}

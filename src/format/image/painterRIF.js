import {Format} from "../../Format.js";

export class painterRIF extends Format
{
	name        = "Painter Raster Image Format";
	website     = "http://fileformats.archiveteam.org/wiki/Painter_RIFF";
	ext         = [".rif"];
	magic       = ["Painter Raster Image Format bitmap", /^x-fmt\/187( |$)/];
	unsupported = true;
}

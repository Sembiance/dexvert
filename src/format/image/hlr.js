import {Format} from "../../Format.js";

export class hlr extends Format
{
	name       = "ZX Spectrum Attributes Gigascreen";
	website    = "http://fileformats.archiveteam.org/wiki/HLR";
	ext        = [".hlr"];
	magic      = ["GigaScreen bitmap"];
	fileSize   = 1628;
	byteCheck  = [{offset : 0, match : [0x76, 0xAF, 0xD3]}];
	notes      = "File is detected as garbage, but it's actually supposed to look that, but because it looks like garbage, we actually want classify to keep identifying it as such: ht - Id-02 (2010) (Hackers Top 2010 Autumn Edition, 7).hlr";
	converters = ["recoil2png"];
}

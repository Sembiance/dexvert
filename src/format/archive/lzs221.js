import {Format} from "../../Format.js";

export class lzs221 extends Format
{
	name       = "LZS221 Compressed";
	website    = "http://fileformats.archiveteam.org/wiki/LZS221";
	packed     = true;
	magic      = ["LZS/Stac compressed data", /^LZS221 archive data/];
	converters = ["deark[module:lzs221]", "lzsdemo"];
}

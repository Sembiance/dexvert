import {Format} from "../../Format.js";

export class gifferQDV extends Format
{
	name       = "Giffer QDV";
	website    = "http://fileformats.archiveteam.org/wiki/QDV_(Giffer)";
	ext        = [".qdv"];
	magic      = ["deark: qdv"];
	weakMagic  = true;
	converters = ["deark[module:qdv]", ...["nconvert", "imageAlchemy", "konvertor"].map(v => `${v}[strongMatch]`)];
}

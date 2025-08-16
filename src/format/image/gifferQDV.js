import {Format} from "../../Format.js";

export class gifferQDV extends Format
{
	name       = "Giffer QDV";
	website    = "http://fileformats.archiveteam.org/wiki/QDV_(Giffer)";
	ext        = [".qdv"];
	magic      = ["deark: qdv", "Qdv :qdv:"];
	weakMagic  = true;
	converters = [
		"deark[module:qdv]", "wuimg[matchType:magic]",
		...["nconvert[format:qdv]", "imageAlchemy", "konvertor"].map(v => `${v}[strongMatch]`)
	];
}

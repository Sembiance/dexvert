import {Format} from "../../Format.js";

export class ttw extends Format
{
	name       = "TTW Compressed File";
	website    = "http://fileformats.archiveteam.org/wiki/TTW";
	ext        = [".cr"];
	magic      = ["TTW Compressed File", "IFF Cruncher compressed data"];
	packed     = true;
	converters = ["xfdDecrunch"];
}

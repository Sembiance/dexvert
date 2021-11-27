import {Format} from "../../Format.js";

export class mng extends Format
{
	name          = "Multiple-image Network Graphics";
	website       = "http://fileformats.archiveteam.org/wiki/MNG";
	ext           = [".mng"];
	mimeType      = "video/x-mng";
	magic         = ["Multiple-image Network Graphics bitmap", "MNG video data"];
	converters    = ["convert[outType:webp]"]
	metaProviders = ["image"];
}

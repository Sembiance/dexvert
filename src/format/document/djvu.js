import {Format} from "../../Format.js";

export class djvu extends Format
{
	name       = "DjVu Document";
	website    = "http://fileformats.archiveteam.org/wiki/DjVu";
	ext        = [".djvu", ".djv"];
	mimeType   = "image/vnd.djvu";
	magic      = ["DjVu multi-page document", "DjVu File Format", "DjVu multiple page document"];
	converters = ["ddjvu"];
}

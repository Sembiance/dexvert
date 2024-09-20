import {Format} from "../../Format.js";

export class djvu extends Format
{
	name       = "DjVu Document";
	website    = "http://fileformats.archiveteam.org/wiki/DjVu";
	ext        = [".djvu", ".djv"];
	mimeType   = "image/vnd.djvu";
	magic      = ["DjVu multi-page document", "DjVu File Format", "DjVu multiple page document", "DjVu single-page document", "DjVu image or single page document", "Format: DjVu document", "Format: Secure DjVu document", "DjVu (gen)",
		"image/vnd.djvu", "image/vnd.djvu+multipage", /^fmt\/(255|318)( |$)/];
	converters = ["ddjvu"];
}

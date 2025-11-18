import {Format} from "../../Format.js";
import {_DJVU_BITMAP_MAGIC} from "../image/djvuBitmap.js#abc";

export class djvu extends Format
{
	name       = "DjVu Document";
	website    = "http://fileformats.archiveteam.org/wiki/DjVu";
	ext        = [".djvu", ".djv"];
	mimeType   = "image/vnd.djvu";
	magic      = [/^DjVu (image or )?(multi-page|multiple page|shared|single-page) document/, "DjVu File Format", "Format: DjVu document", "Format: Secure DjVu document", "DjVu (gen)", "DjVu image or single page document",
		"image/vnd.djvu", "image/vnd.djvu+multipage", /^fmt\/(255|318)( |$)/];
	forbiddenMagic = _DJVU_BITMAP_MAGIC;
	converters     = ["ddjvu"];
}

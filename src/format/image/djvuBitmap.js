import {Format} from "../../Format.js";

const _DJVU_BITMAP_MAGIC = [/^DjVu (color|grayscale) IW44 bitmap/];
export {_DJVU_BITMAP_MAGIC};

export class djvuBitmap extends Format
{
	name       = "DjVu Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/DjVu";
	ext        = [".djvu", ".iw44"];
	mimeType   = "image/vnd.djvu";
	magic      = _DJVU_BITMAP_MAGIC;
	converters = ["ddjvu[outType:png]"];
}

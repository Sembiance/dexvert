import {Format} from "../../Format.js";

export class gif extends Format
{
	name         = "Graphics Interchange Format";
	website      = "http://fileformats.archiveteam.org/wiki/GIF";
	ext          = [".gif"];
	mimeType     = "image/gif";
	magic        = ["GIF image data", /^GIF8[79]a bitmap$/];
	untouched    = r => r.meta.width && r.meta.height;		// if we were able to get our image meta info, then we are a valid GIF and should leave it alone
	metaProvider = ["image", "gifsicle_info"];

	// some GIF files are often corrupted and Imagemagick won't load them, thus no meta data. However nconvert can usually handle them, so we try converting to PNG if no meta data found
	converters = ["nconvert"];
}

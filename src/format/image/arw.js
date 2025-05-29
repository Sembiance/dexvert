import {Format} from "../../Format.js";

export class arw extends Format
{
	name         = "Sony RAW";
	website      = "http://fileformats.archiveteam.org/wiki/Sony_ARW";
	ext          = [".arw"];
	magic        = ["Sony ARW RAW Image File", "Sony digital camera RAW image", /^fmt\/1127( |$)/];
	metaProvider = ["image", "darkTable"];
	converters   = ["darktable_cli", "convert[format:ARW]"];	// nconvert converts anything, like (tiff/pc260001.tif) and (tga/wizard9.arw). abydosconvert also works with mime "image/x-sony-arw" but meh.
}

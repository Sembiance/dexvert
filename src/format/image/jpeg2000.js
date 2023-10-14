import {Format} from "../../Format.js";

export class jpeg2000 extends Format
{
	name         = "JPEG 2000";
	website      = "http://fileformats.archiveteam.org/wiki/JPEG_2000";
	ext          = [".jp2"];
	mimeType     = "image/jp2";
	magic        = ["JPEG 2000", "JP2 (JPEG 2000", "Mac JPEG 2000 bitmap (MacBinary)", /^x-fmt\/392( |$)/];
	metaProvider = ["image"];
	converters   = dexState =>
	{
		const r = [];
		if(dexState.hasMagics("Mac JPEG 2000 bitmap (MacBinary)"))
			r.push("deark[mac][deleteADF][convertAsExt:.jp2]");
		r.push("grk_decompress", "gimp", "convert", "canvas");
		return r;
	};
}

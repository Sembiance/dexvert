import {Format} from "../../Format.js";

export class jpeg2000 extends Format
{
	name         = "JPEG 2000";
	website      = "http://fileformats.archiveteam.org/wiki/JPEG_2000";
	ext          = [".jp2", ".j2c"];
	mimeType     = "image/jp2";
	magic        = ["JPEG 2000", "JP2 (JPEG 2000", "Mac JPEG 2000 bitmap (MacBinary)", "JPEG-2000 Code Stream bitmap", "JPEG 2000 codestream", /^x-fmt\/(392|1794)( |$)/];
	metaProvider = ["image"];
	converters   = dexState =>
	{
		const r = [];
		if(dexState.hasMagics("Mac JPEG 2000 bitmap (MacBinary)"))
			r.push("deark[mac][deleteADF][convertAsExt:.jp2]");
		r.push("grk_decompress", "iconvert", "gimp", "convert", "canvas");
		return r;
	};
}

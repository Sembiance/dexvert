import {Format} from "../../Format.js";

export class jpeg2000 extends Format
{
	name         = "JPEG 2000";
	website      = "http://fileformats.archiveteam.org/wiki/JPEG_2000";
	ext          = [".jp2", ".j2c"];
	mimeType     = "image/jp2";
	magic        = [
		"JPEG 2000", "JP2 (JPEG 2000", "Mac JPEG 2000 bitmap (MacBinary)", "JPEG-2000 Code Stream bitmap", "JPEG 2000 codestream", "image/jp2", "image/x-jp2-codestream", "image/jpm", "piped j2k sequence (j2k_pipe)",
		/^fmt\/(363|463|1794)( |$)/, /^x-fmt\/(392|1794)( |$)/
	];
	idMeta     = ({macFileType}) => macFileType==="jp2k";
	metaProvider = ["image"];
	converters   = dexState =>
	{
		const r = [];
		if(dexState.hasMagics("Mac JPEG 2000 bitmap (MacBinary)"))
			r.push("deark[module:macbinary][mac][deleteADF][convertAsExt:.jp2]");
		r.push("grk_decompress", "iconvert", "ffmpeg[format:j2k_pipe][outType:png]", "gimp", "convert", "wuimg");
		r.push("paintDotNet", "canvas");
		return r;
	};
}

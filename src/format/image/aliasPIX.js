import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class aliasPIX extends Format
{
	name       = "Alias PIX Image";
	website    = "http://fileformats.archiveteam.org/wiki/Alias_PIX";
	ext        = [".pix", ".alias", ".img", ".als"];
	weakExt    = [".pix", ".img"];
	mimeType   = "image/x-alias-pix";
	magic      = ["Alias PIX", "Alias/Wavefront PIX image (alias_pix)", /^fmt\/1092( |$)/];
	converters = ["nconvert", "deark[module:alias_pix]", "gimp", "imconv[format:pix][matchType:magic]", "canvas[matchType:magic]"];
	verify     = async ({inputFile, meta}) =>
	{
		if(inputFile.size<4)
			return false;

		const header = await fileUtil.readFileBytes(inputFile.absolute, 6);
		if(meta.width!==header.getUInt16BE(0) || meta.height!==header.getUInt16BE(2))
			return false;

		return true;
	};
}

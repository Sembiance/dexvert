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
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="APIX" && macFileCreator==="SKET";
	converters = ["nconvert", "deark[module:alias_pix]", "gimp", "imconv[format:pix][matchType:magic]", "canvas[hasExtMatch][matchType:magic]"];
	verify     = async ({inputFile, meta}) =>
	{
		// even with the checks below, there are still false positives so we restrict to less than 2000x2000 as I've never encountered an authentic file this large
		if(inputFile.size<4 || meta.height>2000 || meta.width>2000 || meta.height<2 || meta.width<2)
			return false;

		// Check for probably invalid ratios
		if((meta.width/meta.height)>20 || (meta.height/meta.width)>20)
			return false;

		const header = await fileUtil.readFileBytes(inputFile.absolute, 6);
		if(meta.width!==header.getUInt16BE(0) || meta.height!==header.getUInt16BE(2))
			return false;

		return true;
	};
}

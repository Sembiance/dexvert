import {Format} from "../../Format.js";
import {TEXT_MAGIC_STRONG} from "../../Detection.js";

export class teletext extends Format
{
	name           = "Teletext";
	website        = "http://snisurset.net/code/abydos/teletext.html";
	ext            = [".bin"];
	forbidExtMatch = true;
	forbiddenMagic = TEXT_MAGIC_STRONG;
	mimeType       = "text/x-raw-teletext";
	unsupported    = true;
	notes          = "Can't determine any reliable way to determine if a file is RAW teletext. Abydos will convert any garbage and .bin is far too generic an extension to match on.";
	converters     = [`abydosconvert[format:${this.mimeType}]`];
}

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
	unsupported    = true;	// no reliable way to determine if it's actually RAW teletext or not and abydos will convert anything
	converters     = [`abydosconvert[format:${this.mimeType}]`];
}

import {Format} from "../../Format.js";

export class mrgSystemsText extends Format
{
	name       = "MRG Systems Teletext";
	ext        = [".tti"];
	mimeType   = "text/x.teletext.tti";
	converters = [`abydosconvert[format:${this.mimeType}]`]
}

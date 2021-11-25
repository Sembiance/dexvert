import {Format} from "../../Format.js";

export class cebraText extends Format
{
	name       = "CebraText";
	website    = "http://fileformats.archiveteam.org/wiki/CebraText";
	ext        = [".ttx"];
	magic      = ["Cebra Teletext page"];
	mimeType   = "application/x.teletext.ttx";
	converters = [`abydosconvert[format:${this.mimeType}]`]
}

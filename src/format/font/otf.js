import {Format} from "../../Format.js";
import {imageUtil} from "xutil";

export class otf extends Format
{
	name         = "OpenType Font";
	website      = "http://fileformats.archiveteam.org/wiki/OpenType";
	ext          = [".otf"];
	magic        = ["Format: OpenType - CFF compact font", "font/otf", /^OpenType [Ff]ont/, /^fmt\/520( |$)/];
	metaProvider = ["fc_scan"];
	converters   = ["convert[format:OTF][background:#C0C0C0][matchType:magic]"];
	verify       = async ({newFile}) => (await imageUtil.getInfo(newFile.absolute))?.colorCount>1;
}

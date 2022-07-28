import {Format} from "../../Format.js";

export class aliasPIX extends Format
{
	name       = "Alias PIX Image";
	website    = "http://fileformats.archiveteam.org/wiki/Alias_PIX";
	ext        = [".pix", ".alias", ".img", ".als"];
	weakExt    = true;
	mimeType   = "image/x-alias-pix";
	magic      = ["Alias PIX", /^fmt\/1092( |$)/];
	converters = ["nconvert", "deark", "gimp", "canvas[matchType:magic]"];
	verify     = ({meta}) => meta.width<12000 && meta.height<12000;
}

import {Format} from "../../Format.js";

export class aliasPIX extends Format
{
	name       = "Alias PIX Image";
	website    = "http://fileformats.archiveteam.org/wiki/Alias_PIX";
	ext        = [".pix", ".alias", ".img", ".als"];
	mimeType   = "image/x-alias-pix";
	magic      = ["Alias PIX"];
	converters = ["nconvert", "gimp", "canvas"];
}

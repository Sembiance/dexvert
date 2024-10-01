import {Format} from "../../Format.js";

export class aliasPIX extends Format
{
	name       = "Alias PIX Image";
	website    = "http://fileformats.archiveteam.org/wiki/Alias_PIX";
	ext        = [".pix", ".alias", ".img", ".als"];
	weakExt    = [".pix", ".img"];
	mimeType   = "image/x-alias-pix";
	magic      = ["Alias PIX", "Esm Software PIX bitmap", "Alias/Wavefront PIX image (alias_pix)", /^fmt\/1092( |$)/];
	converters = ["nconvert", "deark[module:alias_pix]", "gimp", "imconv[format:pix][matchType:magic]", "canvas[matchType:magic]"];
	verify     = ({meta}) => meta.width<12000 && meta.height<12000;
}

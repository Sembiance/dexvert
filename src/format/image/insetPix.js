import {Format} from "../../Format.js";

export class insetPix extends Format
{
	name       = "Inset PIX";
	website    = "http://fileformats.archiveteam.org/wiki/Inset_PIX";
	ext        = [".pix"];
	weakExt    = true;
	magic      = ["Inset PIX bitmap", "deark: insetpix"];
	converters = ["deark[module:insetpix]", "hiJaakExpress[matchType:magic][hasExtMatch]"];
}

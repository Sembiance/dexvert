import {Format} from "../../Format.js";

export class fontasyPreview extends Format
{
	name           = "Fontasy Preview";
	website        = "http://fileformats.archiveteam.org/wiki/FONTASY_graphics";
	ext            = [".pv"];
	forbidExtMatch = true;
	magic          = ["FONTASY Preview"];
	weakMagic      = true;
	unsupported    = true;
	//converters     = ["iconvertDOS[format:fontasyPV]"];	// not supported yet, see iconvertDOS.js
}

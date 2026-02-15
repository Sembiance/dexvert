import {Format} from "../../Format.js";

export class loadstarSHP extends Format
{
	name           = "Loadstar SHP";
	website        = "http://fileformats.archiveteam.org/wiki/SHP_(Loadstar)";
	ext            = [".shp"];
	matchPreExt    = true;
	magic          = ["Interpaint bitmap"];	// not actually this format, but often (always?) identifies as such
	weakMagic      = true;
	weakFileSize   = [10018];
	converters     = ["recoil2png[format:SHP]"];
}

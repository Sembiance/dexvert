import {Format} from "../../Format.js";

export class rys extends Format
{
	name       = "Mamut RYS";
	website    = "http://fileformats.archiveteam.org/wiki/Mamut";
	ext        = [".rys"];
	magic      = ["Truevision TGA"];
	weakMagic  = true;
	converters = ["recoil2png[format:RYS]"];
}

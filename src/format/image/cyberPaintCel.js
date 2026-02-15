import {Format} from "../../Format.js";

export class cyberPaintCel extends Format
{
	name       = "Cyber Paint Cell";
	website    = "http://fileformats.archiveteam.org/wiki/Cyber_Paint_Cell";
	ext        = [".cel"];
	magic      = ["Cyber Paint Cell animation"];
	converters = ["recoil2png[format:CEL]"];
}

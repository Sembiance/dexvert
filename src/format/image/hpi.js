import {Format} from "../../Format.js";

export class hpi extends Format
{
	name       = "Hemera Photo Image";
	website    = "http://fileformats.archiveteam.org/wiki/Hemera_Photo-Object";
	ext        = [".hpi"];
	magic      = ["Hemera Photo-Object Image bitmap"];
	notes      = "Kevlar.hpi won't convert for some reason";
	converters = ["nconvert", "deark"];
}

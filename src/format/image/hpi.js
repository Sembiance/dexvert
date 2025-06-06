import {Format} from "../../Format.js";

export class hpi extends Format
{
	name       = "Hemera Photo Image";
	website    = "http://fileformats.archiveteam.org/wiki/Hemera_Photo-Object";
	ext        = [".hpi"];
	magic      = ["Hemera Photo-Object Image bitmap", "deark: hpi", "Hemera Photo Image :hpi:"];
	notes      = "Kevlar.hpi won't convert for some reason";
	converters = ["nconvert[format:hpi]", "deark[module:hpi]"];
}

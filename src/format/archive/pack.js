import {Format} from "../../Format.js";

export class pack extends Format
{
	name       = "Pack Compressed";
	website    = "http://fileformats.archiveteam.org/wiki/Pack_(Unix)";
	ext        = [".z"];
	magic      = ["packed data", "Pack compressed data", "z: Pack"];
	packed     = true;
	converters = ["ancient", "deark[module:pack]"];
}

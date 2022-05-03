import {Format} from "../../Format.js";

export class odg extends Format
{
	name       = "OpenDocument Drawing";
	website    = "http://fileformats.archiveteam.org/wiki/OpenDocument_Drawing";
	ext        = [".odg", ".otg", ".fodg"];
	magic      = ["ZIP Format", "ZIP compressed achive", "Zip archive data", "OpenDocument Drawing Zip", "OpenDocument Graphics document"];
	weakMagic  = ["ZIP Format", "ZIP compressed achive", "Zip archive data"];
	converters = ["soffice[outType:svg]"];
}

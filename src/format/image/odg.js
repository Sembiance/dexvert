import {Format} from "../../Format.js";

export class odg extends Format
{
	name       = "OpenDocument Drawing";
	website    = "http://fileformats.archiveteam.org/wiki/OpenDocument_Drawing";
	ext        = [".odg", ".otg", ".fodg"];
	magic      = ["ZIP Format", "ZIP compressed achive", "Zip archive", "OpenDocument Drawing Zip", "OpenDocument Graphics document", "OpenDocument Drawing Template", "OpenDocument Graphics Template", /^fmt\/(139|296|297)( |$)/];
	weakMagic  = ["ZIP Format", "ZIP compressed achive", "Zip archive"];
	converters = ["soffice[outType:svg]"];
}

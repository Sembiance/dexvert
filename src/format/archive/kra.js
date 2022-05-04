import {Format} from "../../Format.js";

export class kra extends Format
{
	name       = "Krita";
	website    = "http://fileformats.archiveteam.org/wiki/Krita";
	ext        = [".kra"];
	mimeType   = "application/x-krita";
	magic      = [/^Krita [Dd]ocument/, /^fmt\/999( |$)/];
	converters = ["deark"];
}


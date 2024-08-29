import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class sunIcon extends Format
{
	name       = "Sun Icon";
	website    = "http://fileformats.archiveteam.org/wiki/Sun_icon";
	ext        = [".ico", ".icon"];
	magic      = TEXT_MAGIC;
	weakMagic  = true;
	notes      = "Color currently isn't supported. Don't know of a converter that supports it due to palettes not being embedded within the file.";
	converters = ["nconvert", "imconv[format:icon]"];
}

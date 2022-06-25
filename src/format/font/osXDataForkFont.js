import {Format} from "../../Format.js";

export class osXDataForkFont extends Format
{
	name       = "MacOS X Data Fork Font";
	website    = "https://en.wikipedia.org/wiki/Datafork_TrueType";
	ext        = [".dfont"];
	magic      = ["Macintosh OS X Data Fork Font"];
	converters = ["fontforge"];
}

import {Format} from "../../Format.js";

const _OSX_DATA_FORK_FONT_MAGIC = ["Macintosh OS X Data Fork Font"];
export {_OSX_DATA_FORK_FONT_MAGIC};

export class osXDataForkFont extends Format
{
	name       = "MacOS X Data Fork Font";
	website    = "http://fileformats.archiveteam.org/wiki/Data_Fork_Suitcase_font";
	ext        = [".dfont"];
	magic      = _OSX_DATA_FORK_FONT_MAGIC;
	converters = ["fontforge"];
}

import {Format} from "../../Format.js";

const _OSX_DATA_FORK_FONT_MAGIC = ["Macintosh OS X Data Fork Font"];
export {_OSX_DATA_FORK_FONT_MAGIC};

export class osXDataForkFont extends Format
{
	name       = "MacOS X Data Fork Font";
	website    = "https://en.wikipedia.org/wiki/Datafork_TrueType";
	ext        = [".dfont"];
	magic      = _OSX_DATA_FORK_FONT_MAGIC;
	converters = ["fontforge"];
}

import {xu} from "xu";
import {Format} from "../../Format.js";

export class astWii extends Format
{
	name       = "AST Wii Audio";
	website    = "http://fileformats.archiveteam.org/wiki/AST_(Wii)";
	ext        = [".ast"];
	magic      = ["Wii sound data"];
	converters = ["zxtune123", "vgmstream"];
}
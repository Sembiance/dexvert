import {Format} from "../../Format.js";

export class mythosSoftwareLIBArchive extends Format
{
	name       = "Mythos Software LIB Archive";
	website    = "https://moddingwiki.shikadi.net/wiki/LIB_Format_(Mythos_Software)";
	ext        = [".lib"];
	weakExt    = true;
	magic      = ["Mythos Software LIB game data container"];
	converters = ["gamearch"];
}

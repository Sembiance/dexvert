import {Format} from "../../Format.js";

export class mythosSoftwareGameArchive extends Format
{
	name           = "Mythos Software Game Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/LIB_Format_(Mythos_Software)";
	ext            = [".lib"];
	forbidExtMatch = true;
	magic          = ["Mythos Software LIB game data container", /^geArchive: TBD( |$)/];
	converters     = ["gamearch"];
}

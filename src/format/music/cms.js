import {xu} from "xu";
import {Format} from "../../Format.js";

export class cms extends Format
{
	name           = "Creative Music System File";
	website        = "http://fileformats.archiveteam.org/wiki/CMS_(Creative_Music_System)";
	ext            = [".cms"];
	forbidExtMatch = true;
	magic          = ["Creative Music System music"];
	metaProvider   = ["musicInfo"];
	converters     = ["vibe2wav[renameOut]"];
}

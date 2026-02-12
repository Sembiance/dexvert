import {Format} from "../../Format.js";

export class monsterBashGameArchive extends Format
{
	name           = "Monster Bash Game Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/DAT_Format_(Monster_Bash)";
	ext            = [".dat"];
	forbidExtMatch = true;
	filename       = [/^bash\d\.dat$/i];
	converters     = ["gamearch"];
}

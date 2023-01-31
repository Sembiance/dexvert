import {Format} from "../../Format.js";

export class monsterBashDAT extends Format
{
	name       = "Monster Bash DAT Archive";
	website    = "https://moddingwiki.shikadi.net/wiki/DAT_Format_(Monster_Bash)";
	ext        = [".dat"];
	weakExt    = [".dat"];
	filename   = [/^bash\d\.dat$/i];
	converters = ["gamearch"];
}

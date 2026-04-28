import {Format} from "../../Format.js";

export class animationWorks extends Format
{
	name           = "Animation Works Movie";
	ext            = [".awm"];
	forbidExtMatch = true;
	magic          = ["Astound / Animation Works Movie"];
	converters     = ["vibe2avi"];
}

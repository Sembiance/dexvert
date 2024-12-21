import {Format} from "../../Format.js";

export class cyberLinkTalkingShowHeadDefinitionPack extends Format
{
	name           = "CyberLink TalkingShow Head Definition Pack";
	ext            = [".hdp"];
	forbidExtMatch = true;
	magic          = ["CyberLink TalkingShow Head Definition Pack"];
	converters     = ["foremost"];
}

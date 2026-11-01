import {Format} from "../../Format.js";

export class xenophageAlienBloodsportArchive extends Format
{
	name           = "Xenophage: Alien Bloodsport archive";
	ext            = [".xpr"];
	forbidExtMatch = true;
	magic          = [/^geArchive: XPR(_JBR|_2)?( |$)/];
	converters     = ["gameextractor[codes:XPR_JBR,XPR_2,XPR]"];
}

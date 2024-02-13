import {Format} from "../../Format.js";

export class wordStar extends Format
{
	name           = "WordStar Document";
	website        = "http://fileformats.archiveteam.org/wiki/WordStar";
	ext            = [".ws", ".ws3", ".ws5", ".ws7", ".ws2", ".wsd"];
	forbidExtMatch = [".ws"];
	magic          = [/^WordStar .*document/, /^x-fmt\/(205|236|237|261)( |$)/];
	converters     = ["wordStar[matchType:magic]", "fileMerlin", "keyViewPro[outType:pdf]"];
}

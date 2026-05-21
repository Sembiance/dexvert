import {Format} from "../../Format.js";

export class flowCharting extends Format
{
	name           = "Flow Charting";
	website        = "http://fileformats.archiveteam.org/wiki/Flow_Charting";
	ext            = [".cht", ".fcd", ".gfc", ".pdq", ".fc5", ".fcx"];
	forbidExtMatch = true;
	magic          = ["Flow Charting 3 Drawing", /^fmt\/14(06|07|08|09|10|11|12)( |$)/];
	unsupported    = true;	// 483 unique files on discmaster, but these cover multiple format types and major versions, so not really worth supporting at this time
}

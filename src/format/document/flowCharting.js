import {Format} from "../../Format.js";

export class flowCharting extends Format
{
	name           = "Flow Charting";
	website        = "http://fileformats.archiveteam.org/wiki/Flow_Charting";
	ext            = [".cht", ".fcd", ".gfc", ".pdq", ".fc5", ".fcx"];
	forbidExtMatch = true;
	magic          = [/^fmt\/14(06|07|08|09|10|11|12)( |$)/];
	unsupported    = true;
}

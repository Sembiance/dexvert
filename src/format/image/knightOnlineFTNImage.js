import {Format} from "../../Format.js";

export class knightOnlineFTNImage extends Format
{
	name           = "Knight Online FTN Image";
	ext            = [".ftn"];
	forbidExtMatch = true;
	magic          = [/^geViewer: GTT_NTF_FTN_NTF( |$)/];
	converters     = ["gameextractor[renameOut][codes:GTT_NTF_FTN_NTF]"];
}

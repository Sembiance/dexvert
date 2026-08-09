import {Format} from "../../Format.js";

export class easyTrax extends Format
{
	name           = "EasyTrax Module";
	ext            = [".etx"];
	forbidExtMatch = true;
	magic          = ["EasyTrax module"];
	metaProvider   = ["musicInfo"];
	converters     = ["zxtune123", "openmpt123"];
}

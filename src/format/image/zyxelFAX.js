import {Format} from "../../Format.js";

export class zyxelFAX extends Format
{
	name           = "Zyxel FAX";
	ext            = [".fax"];
	forbidExtMatch = true;
	magic          = ["Zyxel FAX format"];
	converters     = ["wuimg"];
}

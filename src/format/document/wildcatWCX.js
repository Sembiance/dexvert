import {Format} from "../../Format.js";

export class wildcatWCX extends Format
{
	name           = "Wildcat! WCX";
	ext            = [".wcx"];
	forbidExtMatch = true;
	magic          = ["Wildcat WCX"];
	weakMagic      = true;
	converters     = ["wccnosy"];
}

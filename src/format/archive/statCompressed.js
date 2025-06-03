import {Format} from "../../Format.js";

export class statCompressed extends Format
{
	name           = "STAT Compressed";
	website        = "https://bellard.org/stat/";
	ext            = [".st"];
	forbidExtMatch = true;
	packed         = true;
	magic          = ["STAT compressed"];
	converters     = ["stat_fabrice"];
}

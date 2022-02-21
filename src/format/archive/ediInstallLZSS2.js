import {Format} from "../../Format.js";

export class ediInstallLZSS2 extends Format
{
	name           = "EDI Install LZSS2 Compressed Data";
	ext            = ["$"];
	forbidExtMatch = true;
	packed         = true;
	magic          = ["EDI Install Pro LZSS2 compressed data"];
	converters     = ["deark"];
}

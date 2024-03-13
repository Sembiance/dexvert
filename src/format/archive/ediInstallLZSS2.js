import {Format} from "../../Format.js";

export class ediInstallLZSS2 extends Format
{
	name           = "EDI Install LZSS2 Compressed Data";
	website        = "http://fileformats.archiveteam.org/wiki/EDI_Install_packed_file";
	ext            = ["$"];
	forbidExtMatch = true;
	packed         = true;
	magic          = ["EDI Install Pro LZSS2 compressed data", "EDI LZSS2 packed"];
	converters     = ["deark[module:edi_pack]"];
}

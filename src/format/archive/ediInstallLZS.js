import {Format} from "../../Format.js";

export class ediInstallLZS extends Format
{
	name           = "EDI Install LZS Compressed Data";
	website        = "http://fileformats.archiveteam.org/wiki/EDI_Install_packed_file";
	ext            = ["$"];
	forbidExtMatch = true;
	magic          = ["EDI Install LZS compressed data", "EDI LZSS packed", "EDI LZSSLib packed"];
	converters     = ["deark[module:edi_pack]", "ediUnpack"];
}

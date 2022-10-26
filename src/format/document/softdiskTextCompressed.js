import {Format} from "../../Format.js";

export class softdiskTextCompressed extends Format
{
	name           = "Softdisk Text Compressor Document";
	website        = "http://justsolve.archiveteam.org/wiki/Softdisk_Text_Compressor";
	ext            = [".ctx"];
	forbidExtMatch = true;
	magic          = ["Softdisk Text Compressor compressed data", /^fmt\/1359( |$)/];
	packed         = true;
	converters     = ["ctx_decompress"];
}

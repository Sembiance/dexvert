import {Format} from "../../Format.js";

export class ediInstallLZS extends Format
{
	name           = "EDI Install LZS Compressed Data";
	ext            = ["$"];
	forbidExtMatch = true;
	magic          = ["EDI Install LZS compressed data"];
	converters     = ["ediUnpack"];
}

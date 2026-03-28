import {Format} from "../../Format.js";

export class rpack extends Format
{
	name           = "RPACK Archive";
	ext            = [".rpack"];
	forbidExtMatch = true;
	magic          = [/^geArchive: RPACK_RP[56]L( |$)/];
	converters     = ["gameextractor[codes:RPACK_RP6L,RPACK_RP5L]"];
}

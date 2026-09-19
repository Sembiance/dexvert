import {Format} from "../../Format.js";

export class eaSCHIAST extends Format
{
	name           = "EA SCHI AST game archive";
	ext            = [".ast"];
	forbidExtMatch = true;
	magic          = [/^geArchive: AST_SCHI( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:AST_SCHI]"];
}

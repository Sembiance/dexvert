import {Format} from "../../Format.js";

export class smallSoldiersSquadCommanderAST extends Format
{
	name           = "Small Soldiers: Squad Commander AST archive";
	ext            = [".ast"];
	forbidExtMatch = true;
	magic          = [/^geArchive: AST( |$)/];
	converters     = ["gameextractor[codes:AST]"];
}

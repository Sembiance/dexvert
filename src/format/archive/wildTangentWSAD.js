import {Format} from "../../Format.js";

export class wildTangentWSAD extends Format
{
	name           = "Wild Tanged WSAD Archive";
	ext            = [".wsad", ".wjp", ".wsbm", ".wsmo", ".wt", ".wsgo", ".wwv", ".wpg"];
	forbidExtMatch = true;
	magic          = [/^geArchive: WSAD_WLD3( |$)/];
	converters     = ["gameextractor[codes:WSAD_WLD3]"];
}

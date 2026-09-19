import {Format} from "../../Format.js";

export class geekCSA extends Format
{
	name           = "GEEK CSA archive";
	ext            = [".csa"];
	forbidExtMatch = true;
	magic          = [/^geArchive: CSA_GEEK( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:CSA_GEEK]"];
}

import {Format} from "../../Format.js";

export class northlandLIBArchive extends Format
{
	name           = "Northland LIB Game archive";
	ext            = [".lib"];
	forbidExtMatch = true;
	magic          = [/^geArchive: LIB_4( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:LIB_4]"];
}

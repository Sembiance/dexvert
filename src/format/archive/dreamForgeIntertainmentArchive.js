import {Format} from "../../Format.js";

export class dreamForgeIntertainmentArchive extends Format
{
	name           = "DreamForge Intertainment archive";
	ext            = [".000", ".001", ".002", ".003", ".004", ".005"];
	forbidExtMatch = true;
	magic          = [/^geArchive: 000_2( |$)/];
	weakMagic 	   = true;
	converters     = ["gameextractor[codes:000_2]"];
}

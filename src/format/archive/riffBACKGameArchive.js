import {Format} from "../../Format.js";

export class riffBACKGameArchive extends Format
{
	name           = "RIFF BACK Game Archive";
	ext            = [".res"];
	forbidExtMatch = true;
	magic          = ["Generic RIFF file BACK", /^geArchive: ZBD_RIFF( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:ZBD_RIFF]"];
}

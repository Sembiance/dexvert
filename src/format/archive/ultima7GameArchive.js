import {Format} from "../../Format.js";

export class ultima7GameArchive extends Format
{
	name           = "Ultima 7 Game Archive";
	ext            = [".vga"];
	forbidExtMatch = true;
	magic          = [/^geArchive: VGA_ULTIMA( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:VGA_ULTIMA]"];
}

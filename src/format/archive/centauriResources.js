import {Format} from "../../Format.js";

export class centauriResources extends Format
{
	name           = "Centauri Resources Archive";
	ext            = [".res"];
	forbidExtMatch = true;
	magic          = [/^geArchive: RES_CENTAURI( |$)/];
	converters     = ["gameextractor[codes:RES_CENTAURI]"];
}

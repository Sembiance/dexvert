import {Format} from "../../Format.js";

export class cryoInteractiveAPC extends Format
{
	name           = "Cryo Interactive APC Audio";
	ext            = [".apc"];
	forbidExtMatch = true;
	magic          = ["Cryo Interactive APC audio", "vgmstream: apc", "CRYO APC (apc)"];
	converters     = ["vgmstream[types:apc]"];
}

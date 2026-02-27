import {Format} from "../../Format.js";

export class dreamfallPAKArchive extends Format
{
	name           = "Dreamfall Archive";
	ext            = [".pak"];
	forbidExtMatch = true;
	magic          = ["dragon: TLJPAK "];
	converters     = ["dragonUnpacker[types:TLJPAK]"];
}

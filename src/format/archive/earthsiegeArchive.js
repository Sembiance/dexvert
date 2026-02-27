import {Format} from "../../Format.js";

export class earthsiegeArchive extends Format
{
	name           = "Earthsiege Archive";
	ext            = [".vol"];
	forbidExtMatch = true;
	magic          = [/^geArchive: VOL_VOLN( |$)/, "dragon: VOL "];
	converters     = ["gameextractor[codes:VOL_VOLN]", "dragonUnpacker[types:VOL]"];
}

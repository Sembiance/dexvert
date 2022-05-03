import {Format} from "../../Format.js";

export class broadBandEBook extends Format
{
	name           = "Broad Band eBook";
	website        = "https://en.wikipedia.org/wiki/BBeB";
	ext            = [".lrf", ".lrx", ".lrs"];
	forbidExtMatch = true;
	magic          = ["BBeB ebook data", "Unencrypted BBeB - BroadBand eBook"];
	converters     = ["ebook_convert"];
}

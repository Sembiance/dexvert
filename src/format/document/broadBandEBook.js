import {Format} from "../../Format.js";

export class broadBandEBook extends Format
{
	name           = "Broad Band eBook";
	website        = "http://fileformats.archiveteam.org/wiki/LRF";
	ext            = [".lrf", ".lrx", ".lrs"];
	forbidExtMatch = true;
	magic          = ["BBeB ebook data", "Unencrypted BBeB - BroadBand eBook", /^fmt\/518( |$)/];
	converters     = ["ebook_convert"];
}

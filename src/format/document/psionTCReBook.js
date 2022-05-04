import {Format} from "../../Format.js";

export class psionTCReBook extends Format
{
	name       = "Psion TCR eBook";
	ext        = [".tcr"];
	magic      = ["Psion TCR eBook", /^fmt\/1099( |$)/];
	converters = ["ebook_convert"];
}

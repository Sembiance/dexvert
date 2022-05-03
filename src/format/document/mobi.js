import {Format} from "../../Format.js";

export class mobi extends Format
{
	name           = "Mobipocket Reader eBook";
	website        = "https://en.wikipedia.org/wiki/Mobipocket";
	ext            = [".mobi", ".prc"];
	forbidExtMatch = true;
	magic          = ["Mobipocket E-book", "Mobipocket - PRC Palm e-Book"];
	converters     = ["ebook_convert"];
}

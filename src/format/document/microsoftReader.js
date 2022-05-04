import {Format} from "../../Format.js";

export class microsoftReader extends Format
{
	name           = "Microsoft Reader eBook";
	website        = "https://en.wikipedia.org/wiki/Microsoft_Reader";
	ext            = [".lit"];
	forbidExtMatch = true;
	magic          = ["Microsoft Reader eBook", /^fmt\/867( |$)/];
	converters     = ["ebook_convert"];
}

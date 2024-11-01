import {Format} from "../../Format.js";

export class amazonKindleBook extends Format
{
	name           = "Amazon Kindle eBook";
	website        = "http://fileformats.archiveteam.org/wiki/AZW";
	ext            = [".azw", ".azw3", ".azw4"];
	forbidExtMatch = true;
	magic          = [/^Amazon Kindle .*eBook/, /^fmt\/1937( |$)/];
	converters     = ["ebook_convert"];
}

import {Format} from "../../Format.js";

export class rocketeBook extends Format
{
	name           = "Rocket eBook";
	website        = "http://fileformats.archiveteam.org/wiki/Rocket_eBook";
	ext            = [".rb"];
	magic          = ["Rocket eBook", /^fmt\/485( |$)/];
	converters     = ["ebook_convert"];
}

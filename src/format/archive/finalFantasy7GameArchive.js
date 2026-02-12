import {Format} from "../../Format.js";

export class finalFantasy7GameArchive extends Format
{
	name           = "Final Fantasy 7 Game Archive";
	ext            = [".lgp"];
	forbidExtMatch = true;
	magic          = ["Final Fantasy Game Archive", /^geArchive: LGP( |$)/];
	converters     = ["gameextractor[codes:LGP]"];
}

import {Format} from "../../Format.js";

export class microsoftXNB extends Format
{
	name           = "Microsoft XNB Archive";
	ext            = [".xnb"];
	forbidExtMatch = true;
	magic          = [/^geArchive: XNB_XNB( |$)/];
	converters     = ["gameextractor[codes:XNB_XNB]"];
}

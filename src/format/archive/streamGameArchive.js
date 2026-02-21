import {Format} from "../../Format.js";

export class streamGameArchive extends Format
{
	name           = "STREAM Game Archive";
	ext            = [".stream"];
	forbidExtMatch = true;
	magic          = [/^geArchive: STREAM( |$)/];
	converters     = ["gameextractor[codes:STREAM]"];
}

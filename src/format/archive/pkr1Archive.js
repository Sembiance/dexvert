import {Format} from "../../Format.js";

export class pkr1Archive extends Format
{
	name           = "PKR1 Archive";
	ext            = [".pkr"];
	forbidExtMatch = true;
	magic          = [/^geArchive: PKR_PKR1( |$)/];
	converters     = ["gameextractor[codes:PKR_PKR1]"];
}

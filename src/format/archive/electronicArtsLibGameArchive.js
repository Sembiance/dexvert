import {Format} from "../../Format.js";

export class electronicArtsLibGameArchive extends Format
{
	name           = "Electronic Arts LIB Game Archive";
	ext            = [".lib"];
	forbidExtMatch = true;
	magic          = ["Electronic Arts LIB container", /^geArchive: LIB_EALIB( |$)/];
	converters     = ["gameextractor[codes:LIB_EALIB]"];
}

import {Format} from "../../Format.js";

export class flflRMIMArchive extends Format
{
	name           = "FLFL RMIN Archive";
	ext            = [".flfl"];
	forbidExtMatch = true;
	magic          = [/^geArchive: FLFL_RMIM( |$)/];
	converters     = ["gameextractor[codes:FLFL_RMIM]"];
}

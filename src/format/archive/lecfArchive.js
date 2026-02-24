import {Format} from "../../Format.js";

export class lecfArchive extends Format
{
	name       = "LECF Archive";
	magic      = [/^geArchive: A_LECF( |$)/];
	converters = ["gameextractor[codes:A_LECF]"];
}

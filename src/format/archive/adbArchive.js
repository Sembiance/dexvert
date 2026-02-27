import {Format} from "../../Format.js";

export class adbArchive extends Format
{
	name           = "ADB Archive";
	ext            = [".adb"];
	forbidExtMatch = true;
	magic          = [/^geArchive: ADB( |$)/];
	converters     = ["gameextractor[codes:ADB]"];
}

import {Format} from "../../Format.js";

export class daveMirraFreestyleBMXZAL extends Format
{
	name           = "Dave Mirra Freestyle BMX ZAL";
	ext            = [".zal"];
	forbidExtMatch = true;
	magic          = [/^geArchive: ZAL_2( |$)/];
	converters     = ["gameextractor[codes:ZAL_2]"];
}

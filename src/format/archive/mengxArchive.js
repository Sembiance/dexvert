import {Format} from "../../Format.js";

export class mengxArchive extends Format
{
	name           = "MENGx Archive";
	ext            = [".mfs"];
	forbidExtMatch = true;
	magic          = [/^geArchive: MFS_MENGXV4( |$)/];
	converters     = ["gameextractor[codes:MFS_MENGXV4]"];
}

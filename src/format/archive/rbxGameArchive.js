import {Format} from "../../Format.js";

export class rbxGameArchive extends Format
{
	name           = "RBX Game Archive";
	ext            = [".rbx"];
	forbidExtMatch = true;
	magic          = [/^geArchive: RBX( |$)/];
	converters     = ["gameextractor[codes:RBX]"];
}

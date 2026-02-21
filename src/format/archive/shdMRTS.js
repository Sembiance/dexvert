import {Format} from "../../Format.js";

export class shdMRTS extends Format
{
	name           = "SHD MRTS Archive";
	ext            = [".str", ".shd", ".ffs"];
	forbidExtMatch = true;
	magic          = [/^geArchive: SHD_MRTS( |$)/];
	converters     = ["gameextractor[codes:SHD_MRTS]"];
}

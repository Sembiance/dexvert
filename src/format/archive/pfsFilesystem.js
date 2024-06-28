import {Format} from "../../Format.js";

export class pfsFilesystem extends Format
{
	name           = "PFS Filesystem";
	ext            = [".img"];
	forbidExtMatch = true;
	magic          = ["PFS Filesystem"];
	converters     = ["binwalk"];
}

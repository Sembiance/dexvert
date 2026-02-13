import {Format} from "../../Format.js";

export class halfLifeMIP extends Format
{
	name           = "Half-Life MIP";
	ext            = [".mip"];
	forbidExtMatch = true;
	magic          = [/^geViewer: WAD_WAD3_MIP( |$)/];
	converters     = ["gameextractor[renameOut][codes:WAD_WAD3_MIP]"];
}

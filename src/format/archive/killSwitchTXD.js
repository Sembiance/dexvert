import {Format} from "../../Format.js";

export class killSwitchTXD extends Format
{
	name           = "Kill Switch TXD";
	ext            = [".txd"];
	forbidExtMatch = true;
	magic          = [/^geArchive: TXD_2( |$)/];
	converters     = ["gameextractor[codes:TXD_2]"];
}

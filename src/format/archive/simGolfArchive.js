import {Format} from "../../Format.js";

export class simGolfArchive extends Format
{
	name           = "Sim Golf archive";
	ext            = [".flg", ".tlp", ".rf"];
	forbidExtMatch = true;
	magic          = [/^geArchive: RF_RCNT( |$)/];
	converters     = ["gameextractor[codes:RF_RCNT]"];
}

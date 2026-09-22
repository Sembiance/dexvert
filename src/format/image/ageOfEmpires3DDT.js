import {Format} from "../../Format.js";

export class ageOfEmpires3DDT extends Format
{
	name           = "Age of Empires 3 DDT Image";
	ext            = [".ddt"];
	forbidExtMatch = true;
	magic          = [/^geViewer: BAR_ESPN_DDT_RTS3( |$)/];
	converters     = ["gameextractor[renameOut][codes:BAR_ESPN_DDT_RTS3]"];
}

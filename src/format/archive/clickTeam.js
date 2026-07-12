import {Format} from "../../Format.js";

export class clickTeam extends Format
{
	name           = "ClickTeam Installer";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Installer: ClickTeam"];
	converters     = ["vibeExtract"];
}

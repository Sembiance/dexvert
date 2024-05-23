import {Format} from "../../Format.js";

export class innoSetupInstaller extends Format
{
	name           = "Inno Setup installer";
	website        = "http://fileformats.archiveteam.org/wiki/Inno_Setup_self-extracting_archive";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Inno Setup installer", "Installer: Inno Setup Module"];
	converters     = ["innounp", "cmdTotal[wcx:InstExpl.wcx]"];
}

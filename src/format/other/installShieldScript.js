import {Format} from "../../Format.js";

export class installShieldScript extends Format
{
	name           = "InstallShield Script";
	website        = "http://fileformats.archiveteam.org/wiki/InstallShield_INS";
	ext            = [".ins"];
	forbidExtMatch = true;
	magic          = ["InstallShield Script"];
	converters     = ["strings"];
}

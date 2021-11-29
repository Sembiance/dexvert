import {Format} from "../../Format.js";

export class installShieldScript extends Format
{
	name           = "InstallShield Script";
	ext            = [".ins"];
	forbidExtMatch = true;
	magic          = ["InstallShield Script"];
	converters     = ["strings"];
}

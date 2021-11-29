import {Format} from "../../Format.js";

export class installShieldPackage extends Format
{
	name           = "InstallShield Package";
	ext            = [".pkg"];
	forbidExtMatch = true;
	magic          = ["InstallShield compiled setup Package"];
	converters     = ["strings"];
}

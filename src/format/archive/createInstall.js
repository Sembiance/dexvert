import {Format} from "../../Format.js";

export class createInstall extends Format
{
	name           = "CreateInstall Installer";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Installer: CreateInstall"];
	converters     = ["vibeExtract"];
}

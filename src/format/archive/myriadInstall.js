import {Format} from "../../Format.js";

export class myriadInstall extends Format
{
	name           = "DeployMaster Installer";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Installer: Myriad Install"];
	converters     = ["vibeExtract"];
}

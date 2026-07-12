import {Format} from "../../Format.js";

export class deployMaster extends Format
{
	name           = "DeployMaster Installer";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Installer: DeployMaster"];
	converters     = ["vibeExtract"];
}

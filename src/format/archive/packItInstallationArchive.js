import {Format} from "../../Format.js";

export class packItInstallationArchive extends Format
{
	name           = "PACKIT Installation Archive";
	ext            = [".ins"];
	forbidExtMatch = true;
	magic          = ["PACKIT Installation Archive"];
	converters     = ["sevenZip"];
}

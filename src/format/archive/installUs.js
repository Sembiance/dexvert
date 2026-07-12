import {Format} from "../../Format.js";

export class installUs extends Format
{
	name           = "InstallUs Installer";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Installer: InstallUs"];
	metaProvider   = ["winedump", "exiftool"];
	converters     = ["vibeExtract"];
}

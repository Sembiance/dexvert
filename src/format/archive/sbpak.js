import {Format} from "../../Format.js";

export class sbpak extends Format
{
	name           = "SBPAK Archive";
	ext            = [".pak"];
	forbidExtMatch = true;
	magic          = [/^geArchive: PAK_SBPAK( |$)/];
	converters     = ["gameextractor[codes:PAK_SBPAK]"];
}

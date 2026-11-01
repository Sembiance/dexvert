import {Format} from "../../Format.js";

export class armobilesDMD extends Format
{
	name           = "Armobiles DMD archive";
	ext            = [".dmd"];
	forbidExtMatch = true;
	magic          = [/^geArchive: DMD_MAGIC( |$)/];
	converters     = ["gameextractor[codes:DMD_MAGIC]"];
}

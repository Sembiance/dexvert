import {Format} from "../../Format.js";

export class fearGameArchive extends Format
{
	name           = "F.E.A.R. game archive";
	ext            = [".arch00", ".arch01", ".arch05"];
	forbidExtMatch = true;
	magic          = ["F.E.A.R. game archive", /^geArchive: ARCH00_LTAR( |$)/];
	converters     = ["gameextractor[codes:ARCH00_LTAR]"];
}

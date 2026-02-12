import {Format} from "../../Format.js";

export class lookingGlassGameArchive extends Format
{
	name           = "Looking Glass Game Archive";
	ext            = [".res"];
	forbidExtMatch = true;
	magic          = ["Looking Glass Resource data", "LG Archiv gefunden", /^geArchive: RES_LG( |$)/];
	converters     = ["gameextractor[codes:RES_LG]"];
}

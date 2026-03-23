import {Format} from "../../Format.js";

export class divinity2Archive extends Format
{
	name           = "Divinity 2 Game Archive";
	ext            = [".dv2"];
	forbidExtMatch = true;
	magic          = [/^geArchive: DV2( |$)/];
	converters     = ["gameextractor[codes:DV2]"];
}

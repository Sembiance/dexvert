import {Format} from "../../Format.js";

export class grandTheftAutoSanAndreasIMGArchive extends Format
{
	name           = "Grand Theft Auto: San Andreas IMG archive";
	ext            = ["img"];
	forbidExtMatch = true;
	magic          = [/^geArchive: IMG_VER2( |$)/];
	converters     = ["gameextractor[codes:IMG_VER2]"];
}

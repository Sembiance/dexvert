import {Format} from "../../Format.js";

export class zAxisGameSoundDataArchive extends Format
{
	name           = "Z-Axis game sound data archive";
	ext            = [".zsd"];
	forbidExtMatch = true;
	magic          = ["Z-Axis game sound data archive", /^geArchive: ZSD_ZSNDWIN( |$)/];
	converters     = ["gameextractor[codes:ZSD_ZSNDWIN]"];
}

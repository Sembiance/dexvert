import {Format} from "../../Format.js";

export class adxAudioPackage extends Format
{
	name           = "ADX Audio Package";
	ext            = [".afs"];
	forbidExtMatch = true;
	magic          = [/^geArchive: AFS_AFS( |$)/];
	converters     = ["gameextractor[codes:AFS_AFS]"];
}

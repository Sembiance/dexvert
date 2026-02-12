import {Format} from "../../Format.js";

export class scummDigitizedSoundsGameArchive extends Format
{
	name           = "SCUMM Digitized Sounds Game Archive";
	ext            = [".sou"];
	forbidExtMatch = true;
	magic          = ["SCUMM digitized Sounds (v5-6)", "Lucasfilm Games VOC Sound", /^geArchive: SOU_SOU( |$)/];
	converters     = ["gameextractor[codes:SOU_SOU]"];
}

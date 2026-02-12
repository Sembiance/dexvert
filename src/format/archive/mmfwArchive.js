import {Format} from "../../Format.js";

export class mmfwArchive extends Format
{
	name           = "MMFW Archive";
	website        = "https://github.com/david47k/mmex";
	ext            = [".mmp", ".mms", ".mmf", ".mma", ".mmb", ".pic", ".snd", ".vec"];
	forbidExtMatch = true;
	magic          = [/^MMFW (Blobs|data|Films|Pictures|Script|Sounds)/, "MMFW resource data", "deark: mmfw (MMFW resource file", /^geArchive: MMP_MMFW( |$)/];
	priority       = this.PRIORITY.LOW;
	converters     = ["deark[module:mmfw]", "gameextractor[codes:MMP_MMFW]"];	// produces garbage: , "mmex"
}

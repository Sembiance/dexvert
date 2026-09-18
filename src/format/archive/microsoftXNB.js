import {Format} from "../../Format.js";

export class microsoftXNB extends Format
{
	name           = "Microsoft XNB Archive";
	ext            = [".xnb"];
	forbidExtMatch = true;
	magic          = [/^geArchive: XNB_XNB( |$)/, "XNA Game Studio (xnb)"];
	converters     = ["gameextractor[codes:XNB_XNB]", "ffmpeg[libre][format:xnb][outType:mp3]"];
}

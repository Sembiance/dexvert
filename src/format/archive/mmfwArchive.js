import {Format} from "../../Format.js";

export class mmfwArchive extends Format
{
	name           = "MMFW Archive";
	website        = "https://github.com/david47k/mmex";
	ext            = [".mmp", ".mms", ".mmf", ".mma", ".mmb", ".pic", ".snd", ".vec"];
	forbidExtMatch = true;
	magic          = [/^MMFW (Blobs|data|Pictures|Scripts|Sounds)/];
	priority       = this.PRIORITY.LOW;
	converters     = ["mmex"];
}

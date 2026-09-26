import {xu} from "xu";
import {Format} from "../../Format.js";

export class projectAftermathDAT extends Format
{
	name           = "Project Aftermath DAT Archive";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = [/^geArchive: DAT_46( |$)/];
	idCheck        = inputFile => inputFile.size>(xu.KB*4);
	priority       = this.PRIORITY.LOW;
	converters     = ["gameextractor[codes:DAT_46]"];
}

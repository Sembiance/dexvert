import {Format} from "../../Format.js";

export class microsoftLesson extends Format
{
	name           = "Microsoft Lesson";
	ext            = [".les", ".lsn"];
	forbidExtMatch = true;
	magic          = ["Microsoft Lesson/tutorial"];
	converters     = ["strings"];
}

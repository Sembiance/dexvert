import {Format} from "../../Format.js";

export class shrinkArchive extends Format
{
	name           = "Shrink Archive";
	ext            = [".shr"];
	forbidExtMatch = true;
	magic          = ["Shrink compressed archive", /^Shrink$/];
	converters     = ["unar"];
}

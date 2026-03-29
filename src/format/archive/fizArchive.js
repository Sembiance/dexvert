import {Format} from "../../Format.js";

export class fizArchive extends Format
{
	name           = "FIZ Archive";
	ext            = [".fiz"];
	forbidExtMatch = true;
	magic          = ["FIZ archive data", "Maximus installer archive format"];
	converters     = ["unFIZ"];
}

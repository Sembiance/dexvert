import {Format} from "../../Format.js";

export class buildEngineGroup extends Format
{
	name           = "Build Engine Group Container";
	ext            = [".grp", ".dat"];
	forbidExtMatch = true;
	magic          = ["Build engine group file", "Build Engine GRP container"];
	converters     = ["gameextractor"];
}

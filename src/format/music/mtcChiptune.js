import {Format} from "../../Format.js";

export class mtcChiptune extends Format
{
	name           = "MTC Chiptune";
	ext            = [".mtc"];
	forbidExtMatch = true;
	magic          = ["MTC chiptune"];
	metaProvider   = ["musicInfo"];
	converters     = ["zxtune123"];
}

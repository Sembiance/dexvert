import {Format} from "../../Format.js";

export class mtcChiptune extends Format
{
	name         = "MTC Chiptune";
	ext          = [".mtc"];
	magic        = ["MTC chiptune"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}

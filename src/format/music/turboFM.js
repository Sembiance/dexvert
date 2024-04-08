import {Format} from "../../Format.js";

export class turboFM extends Format
{
	name         = "TurboFM Compiler Chiptune";
	ext          = [".tfc"];
	magic        = ["TurboFM Compiler chiptune"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}

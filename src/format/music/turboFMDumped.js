import {Format} from "../../Format.js";

export class turboFMDumped extends Format
{
	name         = "TurboFM Dumped";
	ext          = [".tfd"];
	magic        = ["TurboFM Dumped"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}

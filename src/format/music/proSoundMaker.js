import {Format} from "../../Format.js";

export class proSoundMaker extends Format
{
	name         = "Pro Sound Maker";
	ext          = [".psm"];
	magic        = ["Spectrum Pro Sound Maker chiptune"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}

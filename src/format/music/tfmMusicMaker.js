import {Format} from "../../Format.js";

export class tfmMusicMaker extends Format
{
	name         = "TFM Music Maker Module";
	ext          = [".tfe", ".tf0"];
	magic        = ["TFM Music Maker music"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}

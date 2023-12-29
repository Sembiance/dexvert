import {Format} from "../../Format.js";

export class proTracker extends Format
{
	name         = "Pro Tracker";
	website      = "http://fileformats.archiveteam.org/wiki/Pro_Tracker_v1.xx_module";
	ext          = [".pt1", ".pt2", ".pt3"];
	magic        = ["Spectrum Pro Tracker 3 chiptune"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}

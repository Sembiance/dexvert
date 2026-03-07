import {Format} from "../../Format.js";

export class vortexTracker2 extends Format
{
	name         = "Vortex Tracker 2";
	ext          = [".vt2", ".pt3"];
	magic        = ["Vortex Tracker 2 chiptune"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}

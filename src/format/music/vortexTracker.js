import {Format} from "../../Format.js";

export class vortexTracker extends Format
{
	name         = "Vortex Tracker";
	ext          = [".vtx"];
	magic        = ["Vortex Tracker (AY) chiptune"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "ayEmul[matchType:magic]"];
}

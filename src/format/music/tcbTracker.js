import {Format} from "../../Format.js";

export class tcbTracker extends Format
{
	name         = "TCB Tracker Module";
	ext          = [".tcb"];
	magic        = ["TCB Tracker module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "zxtune123"];
}

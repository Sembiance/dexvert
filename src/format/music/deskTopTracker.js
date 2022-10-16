import {Format} from "../../Format.js";

export class deskTopTracker extends Format
{
	name         = "DeskTop Tracker Module";
	ext          = [".dtt"];
	magic        = ["DeskTop Tracker module"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}

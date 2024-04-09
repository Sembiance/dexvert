import {xu} from "xu";
import {Format} from "../../Format.js";

export class eTracker extends Format
{
	name         = "E-Tracker Chiptune";
	ext          = [".etc", ".cop", ".et", ".t", ".saa"];
	magic        = ["E-Tracker chiptune", "E-Tracker (Alt)"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}

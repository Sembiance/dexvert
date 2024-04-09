import {xu} from "xu";
import {Format} from "../../Format.js";

export class extremeTracker extends Format
{
	name          = "Extreme Tracker";
	ext           = [".et1"];
	fileSize      = 112_640;
	matchFileSize = true;
	metaProvider  = ["musicInfo"];
	converters    = ["zxtune123"];
	verify        = ({meta}) => meta.duration>=xu.SECOND;
}

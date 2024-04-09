import {xu} from "xu";
import {Format} from "../../Format.js";

export class sampleTracker extends Format
{
	name         = "Sample Tracker";
	ext          = [".str"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
	verify       = ({meta}) => meta.duration>=(xu.SECOND*5);
}

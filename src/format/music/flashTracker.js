import {xu} from "xu";
import {Format} from "../../Format.js";

export class flashTracker extends Format
{
	name       = "Flash Tracker";
	ext        = [".fls"];
	converters = ["ayEmul"];
	verify     = ({meta}) => meta.duration>=xu.SECOND;
}

import {xu} from "xu";
import {Format} from "../../Format.js";

export class flashTracker extends Format
{
	name       = "Flash Tracker";
	ext        = [".fls"];
	idCheck    = inputFile => inputFile.size<9999;	// all sample files I have (none from discmaster exist) are less than 10,000 bytes (largest I have is 6,652)
	converters = ["ayEmul"];
	verify     = ({meta}) => meta.duration>=xu.SECOND;
}

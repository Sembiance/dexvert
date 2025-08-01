import {xu} from "xu";
import {Format} from "../../Format.js";

export class sampleTracker extends Format
{
	name         = "Sample Tracker";
	ext          = [".str"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
	verify       = ({meta}) => meta.duration>=(xu.SECOND*5);
	unsupported  = true;	// Very rare, no samples found on discmaster for example, so with just a .str match and that zxtune123 converts random garbage, mark it unsupported
}

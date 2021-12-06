import {Format} from "../../Format.js";

export class famiTracker extends Format
{
	name        = "FamiTracker Module";
	ext         = [".fmt"];
	magic       = ["FamiTracker module"];
	unsupported = true;
	notes       = "Can maybe support this by running FamiTracker for windows and seeing if it has a converter: http://famitracker.com/";
}

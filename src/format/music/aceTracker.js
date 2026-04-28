import {Format} from "../../Format.js";

export class aceTracker extends Format
{
	name        = "Ace Tracker Module";
	ext         = [".am"];
	magic       = ["Ace Tracker module"];
	unsupported = true;	// only 26 unique files on discmaster. A vibe created converter was started, but abandoned see vibe/legacy/aceTracker
}

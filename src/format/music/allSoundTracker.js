import {Format} from "../../Format.js";

export class allSoundTracker extends Format
{
	name        = "All Sound Tracker Module";
	ext         = [".ast"];
	magic       = ["All Sound Tracker module"];
	unsupported = true;	// only 16 unique files on discmaster, vibe converter stated but abandoned in vibe/legacy/allSoundTracker
}

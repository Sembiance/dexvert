import {Format} from "../../Format.js";

// double ll is not a typo
export class pollyTracker extends Format
{
	name        = "PollyTracker Module";
	ext         = [".mod"];
	magic       = ["Polly Tracker module"];
	unsupported = true;	// only 1 unique file on discmaster
}

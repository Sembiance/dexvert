import {Format} from "../../Format.js";

export class vicTracker extends Format
{
	name        = "Vic-Tracker Module";
	ext         = [".vt"];
	magic       = ["Vic-Tracker module"];
	unsupported = true;	// only 5 unique files on discmaster
}

import {Format} from "../../Format.js";

export class famiTracker extends Format
{
	name        = "FamiTracker Module";
	ext         = [".fmt"];
	magic       = ["FamiTracker module"];
	unsupported = true;
	notes       = "I tried using FamiTracker under WinXP http://famitracker.com/ but it just created a WAV of zero bytes long. Maybe because I'm not emulating a sound card...";
}

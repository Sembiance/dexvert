import {Format} from "../../Format.js";

export class screamTrackerSample extends Format
{
	name           = "Scream Tracker Sample";
	ext            = [".snd", ".s3i", ".smp"];
	forbidExtMatch = true;
	magic          = ["Scream Tracker Sample", "Scream Tracker/Digiplayer sample"];
	converters     = ["awaveStudio"];
}

import {Format} from "../../Format.js";

export class svarTracker extends Format
{
	name        = "SVArTracker Module";
	ext         = [".svar"];
	magic       = ["SVArTracker module"];
	unsupported = true;
}

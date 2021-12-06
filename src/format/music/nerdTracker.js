import {Format} from "../../Format.js";

export class nerdTracker extends Format
{
	name        = "NerdTracker Module";
	ext         = [".ned"];
	magic       = ["Nerdtracker II module"];
	unsupported = true;
}

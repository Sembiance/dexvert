import {Format} from "../../Format.js";

export class mvsTracker extends Format
{
	name        = "MVSTracker Module";
	ext         = [".mus"];
	magic       = ["MVSTracker Music module"];
	unsupported = true;
}

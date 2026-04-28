import {Format} from "../../Format.js";

export class ramTracker extends Format
{
	name        = "RamTracker Module";
	ext         = [".trk"];
	magic       = ["RamTracker module"];
	unsupported = true;	// only 11 unique files on discmaster
}

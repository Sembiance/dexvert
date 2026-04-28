import {Format} from "../../Format.js";

export class proTrekkr extends Format
{
	name        = "Pro Trekkr Module";
	ext         = [".ptk"];
	magic       = ["Pro Trekkr module", "Pro Trekkr 2.0 module"];
	unsupported = true;	// 0 files on discmaster
}

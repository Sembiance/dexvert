import {Format} from "../../Format.js";

export class starkos extends Format
{
	name        = "STarKos Module";
	ext         = [".psy"];
	magic       = ["STarKos song"];
	unsupported = true;	// only 61 unique files on discmaster
}

import {Format} from "../../Format.js";

export class sunVox extends Format
{
	name        = "SunVox Module";
	ext         = [".psy"];
	magic       = ["SunVox module"];
	unsupported = true;	// only 105 unique files on discmaster
}

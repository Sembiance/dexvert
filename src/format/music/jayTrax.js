import {Format} from "../../Format.js";

export class jayTrax extends Format
{
	name        = "JayTrax Module";
	ext         = [".jxs"];
	magic       = ["JayTrax module"];
	unsupported = true;	// only 56 unique files on discmaster, likely less due to false positives
}

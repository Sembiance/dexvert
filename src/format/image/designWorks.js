import {Format} from "../../Format.js";

export class designWorks extends Format
{
	name        = "DesignWorks Drawing";
	magic       = ["DesignWorks drawing"];
	unsupported = true;	// only 10 unique files on discmaster
}

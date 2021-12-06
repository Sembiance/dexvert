import {Format} from "../../Format.js";

export class sbStudio extends Format
{
	name        = "SBStudio Module";
	ext         = [".pac"];
	magic       = ["SBStudio module"];
	unsupported = true;
}

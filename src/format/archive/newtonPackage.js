import {xu} from "xu";
import {Format} from "../../Format.js";

export class newtonPackage extends Format
{
	name        = "Newton Package";
	ext         = [".pkg"];
	magic       = ["Newton Package"];
	unsupported = true;
}

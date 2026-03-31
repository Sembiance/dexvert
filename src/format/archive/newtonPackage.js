import {xu} from "xu";
import {Format} from "../../Format.js";

export class newtonPackage extends Format
{
	name           = "Newton Package";
	ext            = [".pkg"];
	forbidExtMatch = true;
	magic          = ["Newton Package"];
	converters     = ["vibeExtract"];
}

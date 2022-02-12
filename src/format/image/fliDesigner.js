import {Format} from "../../Format.js";

export class fliDesigner extends Format
{
	name       = "FLI Designer";
	ext        = [".fli"];
	converters = ["recoil2png", "view64"];
}

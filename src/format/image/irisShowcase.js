import {Format} from "../../Format.js";

export class irisShowcase extends Format
{
	name        = "IRIS Showcase Presentation/Drawing";
	ext         = [".sc", ".showcase"];
	magic       = ["IRIS Showcase file", "IRIS Showcase drawing"];
	unsupported = true;
}

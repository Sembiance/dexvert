import {Format} from "../../Format.js";

export class noiseRunner extends Format
{
	name        = "NoiseRunner Module";
	ext         = [".nr"];
	magic       = ["NoiseRunner song/module"];
	unsupported = true;
}

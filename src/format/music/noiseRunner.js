import {Format} from "../../Format.js";

export class noiseRunner extends Format
{
	name           = "NoiseRunner Module";
	ext            = [".nru", ".nr"];
	forbidExtMatch = true;
	magic          = ["NoiseRunner song/module"];
	converters     = ["uade123", "xmp"];
}

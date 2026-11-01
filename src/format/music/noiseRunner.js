import {Format} from "../../Format.js";

export class noiseRunner extends Format
{
	name           = "NoiseRunner Module";
	ext            = [".nru", ".nr"];
	forbidExtMatch = true;
	magic          = ["NoiseRunner song/module", "NoiseRunner module"];
	weakMagic      = true;
	converters     = ["uade123", "xmp"];	// glitchy: "openmpt123"
}

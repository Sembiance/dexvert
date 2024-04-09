import {Format} from "../../Format.js";

export class atariDigiMix extends Format
{
	name       = "Atari Digi-Mix Module";
	ext        = [".mix"];
	magic      = ["Atari Digi-Mix module"];
	converters = ["ym2wav"];
}

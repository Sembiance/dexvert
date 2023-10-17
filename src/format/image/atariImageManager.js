import {Format} from "../../Format.js";

export class atariImageManager extends Format
{
	name       = "Atari Image Manager";
	ext        = [".col", ".im"];
	converters = ["recoil2png"];
}

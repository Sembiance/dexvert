import {Format} from "../../Format.js";

export class atariImageManager extends Format
{
	name       = "Atari Image Manager";
	ext        = [".col", ".im"];
	idCheck    = inputFile => inputFile.size%16384===0;
	converters = ["recoil2png"];
}

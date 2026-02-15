import {Format} from "../../Format.js";

export class atariImageManager extends Format
{
	name       = "Atari Image Manager";
	ext        = [".col", ".im"];
	magic      = ["AIM :aim:"];
	idCheck    = inputFile => inputFile.size%16384===0;
	converters = ["recoil2png[format:IM,COL]", "nconvert[format:aim]"];
}

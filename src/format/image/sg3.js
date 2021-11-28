import {Format} from "../../Format.js";

export class sg3 extends Format
{
	name       = "Atari Standard Graphics 3";
	website    = "http://fileformats.archiveteam.org/wiki/Standard_Graphics_3_(Atari)";
	ext        = [".sg3"];
	converters = ["recoil2png"];
}

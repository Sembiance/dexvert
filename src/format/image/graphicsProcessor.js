import {Format} from "../../Format.js";

export class graphicsProcessor extends Format
{
	name       = "Graphics Processor";
	website    = "http://fileformats.archiveteam.org/wiki/Graphics_Processor";
	ext        = [".pg1", ".pg2", ".pg3"];
	fileSize   = 32331;
	converters = ["recoil2png"];
}

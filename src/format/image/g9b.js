import {Format} from "../../Format.js";

export class g9b extends Format
{
	name       = "GFX9k G9B";
	website    = "http://fileformats.archiveteam.org/wiki/G9B";
	ext        = [".g9b"];
	magic      = ["G9B graphics format bitmap"];
	converters = ["recoil2png"];
}

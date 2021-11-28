import {Format} from "../../Format.js";

export class rembrandt extends Format
{
	name       = "Rembrandt True Color Picture";
	website    = "http://fileformats.archiveteam.org/wiki/Rembrandt";
	ext        = [".tcp"];
	magic      = ["Rembrandt True Color Picture bitmap"];
	converters = ["recoil2png"];
}

import {Format} from "../../Format.js";

export class neutralFileFormat extends Format
{
	name       = "Neutral File Format";
	website    = "http://fileformats.archiveteam.org/wiki/NFF";
	ext        = [".nff"];
	converters = ["assimp"];
}

import {Format} from "../../Format.js";

export class sbStudio extends Format
{
	name       = "SBStudio Module";
	website    = "http://fileformats.archiveteam.org/wiki/SBStudio_module";
	ext        = [".pac"];
	magic      = ["SBStudio module"];
	converters = ["pacplay"];
}

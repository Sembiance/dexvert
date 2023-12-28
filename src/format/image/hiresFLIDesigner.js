import {Format} from "../../Format.js";

export class hiresFLIDesigner extends Format
{
	name       = "Hires FLI Designer";
	website    = "http://fileformats.archiveteam.org/wiki/Hires_FLI_Designer";
	ext        = [".hfc", ".hfd"];
	converters = ["recoil2png"];
}

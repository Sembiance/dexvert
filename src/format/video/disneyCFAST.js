import {Format} from "../../Format.js";

export class disneyCFAST extends Format
{
	name       = "Disney Animation Studio CFAST";
	website    = "http://fileformats.archiveteam.org/wiki/CFAST_Disney_Animation_Studio";
	ext        = [".cft", ".sec"];
	magic      = ["CFast Animation", "Disney Animation Studio Secure Animation"];
	notes      = "The format is documented, so someone could create a more modern converter";
	converters = ["flick"];
}

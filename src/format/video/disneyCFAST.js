import {Format} from "../../Format.js";

export class disneyCFAST extends Format
{
	name       = "Disney Animation Studio CFAST";
	website    = "http://justsolve.archiveteam.org/wiki/CFAST_Disney_Animation_Studio";
	ext        = [".cft"];
	magic      = ["CFast Animation"];
	notes      = "The format is documented, so someone could create a more modern converter";
	converters = ["flick"];
}

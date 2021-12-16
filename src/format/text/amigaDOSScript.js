import {Format} from "../../Format.js";

export class amigaDOSScript extends Format
{
	name         = "AmigaDOS Script File";
	website      = "https://amigasourcecodepreservation.gitlab.io/mastering-amigados-scripts/";
	magic        = ["AmigaDOS script"];
	untouched    = true;
	metaProvider = ["text"];
}

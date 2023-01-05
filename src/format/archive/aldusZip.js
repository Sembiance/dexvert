import {Format} from "../../Format.js";

export class aldusZip extends Format
{
	name        = "Aldus Zip Compressed File";
	magic       = ["Aldus Zip compressed installation data"];
	unsupported = true;
	notes       = "No known extractor program.";
}

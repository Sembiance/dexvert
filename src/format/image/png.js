import {Format} from "../../Format.js";

export class png extends Format
{
	name          = "Portable Network Graphic";
	website       = "http://fileformats.archiveteam.org/wiki/PNG";
	ext           = [".png"];
	mimeType      = "image/png";
	magic         = ["Portable Network Graphics", "PNG image data"];
	untouched     = true;
	fallback      = true;
	metaProviders = ["image"];
}

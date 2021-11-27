import {Format} from "../../Format.js";

export class palmDatabase extends Format
{
	name          = "Palm Database ImageViewer format";
	website       = "http://fileformats.archiveteam.org/wiki/Palm_Database_ImageViewer";
	ext           = [".pdb"];
	magic         = ["Palm FireViewer bitmap", "FireViewer/ImageViewer PalmOS document", "Palm Pilot bitmap"];
	converters    = ["convert", "nconvert"]
	metaProviders = ["image"];
}

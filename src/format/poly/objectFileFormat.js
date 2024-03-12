import {Format} from "../../Format.js";

export class objectFileFormat extends Format
{
	name       = "Geomview Object File Format";
	website    = "http://fileformats.archiveteam.org/wiki/OFF_(Geomview_Object_File_Format)";
	ext        = [".off"];
	magic      = ["OFF geometry definition"];
	converters = ["assimp"];
}

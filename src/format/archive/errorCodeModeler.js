import {Format} from "../../Format.js";

export class errorCodeModeler extends Format
{
	name       = "Error Code Modeler";
	website    = "http://fileformats.archiveteam.org/wiki/Error_Code_Modeler";
	ext        = [".ecm"];
	magic      = ["Error Code Modeler"];
	weakMagic  = true;
	converters = ["unecm"];
}

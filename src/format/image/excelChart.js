import {Format} from "../../Format.js";

export class excelChart extends Format
{
	name        = "Excel Chart";
	website     = "http://fileformats.archiveteam.org/wiki/Ascii-Art_Editor";
	ext         = [".xlc"];
	magic       = ["Microsoft Excel", /^fmt\/(553|554)( |$)/];
	weakMagic   = ["Microsoft Excel"];
	unsupported = true;
	notes       = "Canvas claims support for this, but I couldn't get it to convert any of my samples.";
}

import {Format} from "../../Format.js";

export class excelChart extends Format
{
	name        = "Excel Chart";
	website     = "http://fileformats.archiveteam.org/wiki/Ascii-Art_Editor";
	ext         = [".xlc"];
	magic       = ["Microsoft Excel", /^fmt\/(553|554)( |$)/, /^x-fmt\/126( |$)/];
	weakMagic   = ["Microsoft Excel"];
	unsupported = true;
	notes       = "Canvas and KeyView Pro both claim support for this, but I couldn't get them to convert any of my samples.";
}

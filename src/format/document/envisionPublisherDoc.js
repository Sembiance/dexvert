import {xu} from "xu";
import {Format} from "../../Format.js";

export class envisionPublisherDoc extends Format
{
	name        = "Envision Publisher Document";
	website     = "http://fileformats.archiveteam.org/wiki/Envision_Publisher";
	ext         = [".evp", ".evt"];
	magic       = ["EnVision Publisher DTP document", /^fmt\/1580( |$)/];
	unsupported = true;	// only 46 unique files on discmaster, almost all just samples distributed with the program
	notes       = `Envision Publisher for MSDOS doesn't have an "Export" option. So either vibe code a converter or set up DOSBOX PDF Printer emulation: superuser.com/questions/270457/how-can-i-print-with-dosbox`;
}

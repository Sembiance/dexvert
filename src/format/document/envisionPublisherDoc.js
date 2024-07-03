import {xu} from "xu";
import {Format} from "../../Format.js";

export class envisionPublisherDoc extends Format
{
	name        = "Envision Publisher Document";
	website     = "http://fileformats.archiveteam.org/wiki/Envision_Publisher";
	ext         = [".evp", ".evt"];
	magic       = ["EnVision Publisher DTP document", /^fmt\/1580( |$)/];
	unsupported = true;
	notes       = xu.trim`
		Envision Publisher for MSDOS doesn't have an "Export" option.
		I could figure out how to 'print to a file' or I could set up DOSBOX PDF Printer emulation: superuser.com/questions/270457/how-can-i-print-with-dosbox`;
}

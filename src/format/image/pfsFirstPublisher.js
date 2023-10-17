import {Format} from "../../Format.js";

export class pfsFirstPublisher extends Format
{
	name         = "PFS First Publisher";
	website      = "http://fileformats.archiveteam.org/wiki/ART_(PFS:_First_Publisher)";
	ext          = [".art"];
	metaProvider = ["image"];
	converters   = ["deark[module:fp_art]", "nconvert", "convert"];
}

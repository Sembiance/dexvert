import {Format} from "../../Format.js";

export class pfsFirstPublisher extends Format
{
	name         = "PFS First Publisher";
	website      = "http://fileformats.archiveteam.org/wiki/ART_(PFS:_First_Publisher)";
	ext          = [".art"];
	byteCheck    = [{offset : 0, match : [0x00, 0x00]}, {offset : 4, match : [0x00, 0x00]}];
	metaProvider = ["image"];
	converters   = ["deark[module:fp_art]", "nconvert", "convert"];
}

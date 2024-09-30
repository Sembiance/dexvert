import {Format} from "../../Format.js";

export class structuredFax extends Format
{
	name       = "Structured Fax";
	ext        = [".sff"];
	website    = "http://fileformats.archiveteam.org/wiki/Acorn_Draw";
	magic      = ["structured fax file", "Structured Fax Format bitmap"];
	converters = ["nconvertWine", "irfanView"];
}

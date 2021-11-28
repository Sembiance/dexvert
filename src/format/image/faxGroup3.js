import {Format} from "../../Format.js";

export class faxGroup3 extends Format
{
	name         = "CCITT Fax Group 3";
	website      = "http://fileformats.archiveteam.org/wiki/CCITT_Group_3";
	ext          = [".g3"];
	mimeType     = "image/g3fax";
	metaProvider = ["image"];
	converters   = ["nconvert", `abydosconvert[format:${this.mimeType}]`, "convert"];
}

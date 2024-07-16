import {Format} from "../../Format.js";

export class pogNames extends Format
{
	name       = "Print Shop Graphic POG Archive Names File";
	website    = "http://fileformats.archiveteam.org/wiki/PrintMaster";
	ext        = [".pnm"];
	auxFiles   = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.pog`);
	slow       = true;
	converters = ["strings"];
}

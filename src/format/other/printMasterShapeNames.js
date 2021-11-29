import {Format} from "../../Format.js";

export class printMasterShapeNames extends Format
{
	name       = "PrintMaster Shape Names";
	website    = "http://fileformats.archiveteam.org/wiki/PrintMaster";
	ext        = [".sdr"];
	auxFiles   = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.shp`);
	converters = ["strings"];
}

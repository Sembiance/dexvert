import {Format} from "../../Format.js";

export class rcaVOC extends Format
{
	name       = "RCA-VOC";
	website    = "http://fileformats.archiveteam.org/wiki/RCA-VOC";
	ext        = [".voc"];
	magic      = ["RCA digital voice recorder audio"];
	converters = ["devoc"];
}

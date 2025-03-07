import {Format} from "../../Format.js";

export class xRes extends Format
{
	name       = "xRes Image";
	website    = "http://fileformats.archiveteam.org/wiki/XRes";
	ext        = [".lrg"];
	magic      = ["xRes multi-resolution bitmap"];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="LRG " && macFileCreator==="xRes";
	converters = ["xRes"];
}

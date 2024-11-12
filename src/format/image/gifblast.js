import {Format} from "../../Format.js";

export class gifblast extends Format
{
	name       = "GIFBLAST Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/GIFBLAST";
	ext        = [".gfb"];
	magic      = ["GIFBLAST bitmap"];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="GFBf" && macFileCreator==="MGFB";
	converters = ["gifblast"];
}

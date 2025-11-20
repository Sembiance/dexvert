import {Format} from "../../Format.js";

export class electricImage extends Format
{
	name       = "Electric Image";
	magic      = ["Electric Image :eidi:"];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="EIDI" && macFileCreator==="EIAD";
	converters = ["nconvert[format:eidi] -> convert[removeAlpha]"];
}

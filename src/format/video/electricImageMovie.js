import {Format} from "../../Format.js";

export class electricImageMovie extends Format
{
	name       = "Electic Image Movie";
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="EIDI" && macFileCreator==="EIAD";
	converters = ["na_eofdec[format:electricimg]"];
}

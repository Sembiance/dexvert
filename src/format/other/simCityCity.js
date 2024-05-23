import {Format} from "../../Format.js";

export class simCityCity extends Format
{
	name        = "SimCity City";
	ext         = [".cty"];
	magic       = ["SimCity City"];
	unsupported = true;
	idMeta      = ({macFileType, macFileCreator}) => macFileType==="CITY" && macFileCreator==="MCRP";
}

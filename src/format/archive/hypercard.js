import {Format} from "../../Format.js";

export class hypercard extends Format
{
	name       = "HyperCard Stack";
	website    = "http://fileformats.archiveteam.org/wiki/HyperCard_stack";
	magic      = ["HyperCard Stack", /^fmt\/1490( |$)/];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="STAK" && macFileCreator==="WILD";
	converters = ["hypercard_dasm & stackimport"];
}

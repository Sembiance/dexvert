import {Format} from "../../Format.js";

export class hypercard extends Format
{
	name       = "HyperCard Stack";
	website    = "http://fileformats.archiveteam.org/wiki/HyperCard_stack";
	magic      = ["HyperCard Stack", /^fmt\/1490( |$)/];
	idMeta     = ({macFileType}) => macFileType==="STAK";	// I used to check a ton of different creators, but it's just too many, so just check for STAK file type
	converters = ["hypercard_dasm & stackimport"];
}

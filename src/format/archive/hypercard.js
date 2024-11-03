import {Format} from "../../Format.js";

export class hypercard extends Format
{
	name       = "HyperCard Stack";
	website    = "http://fileformats.archiveteam.org/wiki/HyperCard_stack";
	magic      = ["HyperCard Stack", /^fmt\/1490( |$)/];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="STAK" && ["gPA2", "WILD"].includes(macFileCreator);
	converters = ["hypercard_dasm & stackimport"];
}

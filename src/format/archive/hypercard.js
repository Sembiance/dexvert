import {Format} from "../../Format.js";

export class hypercard extends Format
{
	name       = "HyperCard Stack";
	website    = "http://fileformats.archiveteam.org/wiki/HyperCard_stack";
	magic      = ["HyperCard Stack", /^fmt\/1490( |$)/];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="STAK" && ["BILL", "FMPR", "gPA2", "MACA", "MWPR", "PLUS", "WILD", "Wild"].includes(macFileCreator);
	converters = ["hypercard_dasm & stackimport"];
}

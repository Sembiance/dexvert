import {Format} from "../../Format.js";

export class writeNow extends Format
{
	name       = "WriteNow Document";
	website    = "http://fileformats.archiveteam.org/wiki/WriteNow";
	magic      = ["WriteNow document", /^fmt\/799( |$)/];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="nX^2" && macFileCreator==="nX^n";
	converters = ["soffice[format:WriteNow]", "wordForWord"];
}

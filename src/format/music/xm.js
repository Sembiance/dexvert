import {Format} from "../../Format.js";

export class xm extends Format
{
	name         = "Extended Module";
	website      = "http://fileformats.archiveteam.org/wiki/Extended_Module";
	ext          = [".xm", ".oxm"];
	magic        = ["Fasttracker II module sound data", "FastTracker 2 eXtended Module", "audio/x-xm", /^fmt\/323( |$)/];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="XM  " && ["MOD!", "SNPL"].includes(macFileCreator);
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123"];
}

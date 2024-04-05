import {Format} from "../../Format.js";

export class diskDoubler extends Format
{
	name         = "Disk Doubler";
	website      = "http://justsolve.archiveteam.org/wiki/DiskDoubler";
	ext          = [".dd"];
	keepFilename = true;
	magic        = ["Disk Doubler compressed data", "DiskDoubler compressed data", /^DiskDoubler$/, /^fmt\/1399( |$)/];
	macMeta      = ({macFileType, macFileCreator}) => ["DDFL", "DD01", "DDF2", "DDF3"].includes(macFileType) && macFileCreator==="DDAP";
	converters   = ["unar[mac]", "macunpack"];
}

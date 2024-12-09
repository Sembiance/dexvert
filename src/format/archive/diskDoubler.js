import {Format} from "../../Format.js";

export class diskDoubler extends Format
{
	name         = "Disk Doubler";
	website      = "http://justsolve.archiveteam.org/wiki/DiskDoubler";
	ext          = [".dd"];
	keepFilename = true;
	magic        = ["Disk Doubler compressed data", "DiskDoubler compressed data", "DDA2 Self-Extracting-Archive", /^DiskDoubler$/, /^fmt\/1399( |$)/];
	idMeta       = ({macFileType, macFileCreator}) => ["DDAR", "DDfc", "DDfj", "DDFL", "DD01", "DDf0", "DDF0", "DDF1", "DDF2", "DDf3", "DDF3", "DDF4", "DDF5", "DDF6", "DDfh", "DDfr"].includes(macFileType) && macFileCreator==="DDAP";
	converters   = ["unar[mac]", "macunpack"];
}

import {Format} from "../../Format.js";

export class diskDoubler extends Format
{
	name         = "Disk Doubler";
	website      = "http://justsolve.archiveteam.org/wiki/DiskDoubler";
	ext          = [".dd"];
	keepFilename = true;
	magic        = ["Disk Doubler compressed data", "DiskDoubler compressed data", "DDA2 Self-Extracting-Archive", /^DiskDoubler$/, /^fmt\/1399( |$)/];
	idMeta       = ({macFileCreator}) => macFileCreator==="DDAP";
	converters   = ["unar[mac]", "macunpack"];
}

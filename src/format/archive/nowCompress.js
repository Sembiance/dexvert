import {Format} from "../../Format.js";

export class nowCompress extends Format
{
	name       = "Now Compress";
	website    = "http://fileformats.archiveteam.org/wiki/Now_Compress";
	magic      = ["Now Compress"];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="INSA" && macFileCreator==="iNow";
	converters = ["unar[mac][type:Now Compress]"];
}

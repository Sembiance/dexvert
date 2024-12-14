import {Format} from "../../Format.js";

export class palmResource extends Format
{
	name       = "Palm Resource";
	website    = "http://fileformats.archiveteam.org/wiki/PRC_(Palm_OS)";
	ext        = [".prc"];
	magic      = ["Palm Pilot executable"];
	idMeta     = ({macFileType, macFileCreator}) => (macFileType==="PRC " && ["PPia", "PITT", "SIfP"].includes(macFileCreator)) || (macFileType==="Gld0 " && macFileCreator==="Gld1");
	converters = ["deark[module:palmdb]"];
}

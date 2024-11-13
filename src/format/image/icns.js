import {Format} from "../../Format.js";

export class icns extends Format
{
	name       = "MacOS Icon";
	website    = "http://fileformats.archiveteam.org/wiki/ICNS";
	ext        = [".icns"];
	mimeType   = "image/x-icns";
	magic      = ["Mac OS X icon", "Apple Icon Image Format", "image/x-icns", /^fmt\/1185( |$)/];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="ICNS" && macFileCreator==="Mngl";
	converters = ["deark[module:icns]", "iio2png", `abydosconvert[format:${this.mimeType}]`];
}

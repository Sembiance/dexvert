import {Format} from "../../Format.js";

export class aolART extends Format
{
	name       = "AOL ART Compressed Image";
	website    = "http://fileformats.archiveteam.org/wiki/ART_(AOL_compressed_image)";
	ext        = [".art"];
	magic      = ["AOL ART image", "AOL ART (Johnson-Grace compressed) bitmap", /^fmt\/666( |$)/];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="ARTf" && macFileCreator==="AOqc";
	converters = ["aolart2ppm2015", "aolart2ppm2007", "graphicWorkshopProfessional"];
}

import {Format} from "../../Format.js";

export class macOSSelfMountingImage extends Format
{
	name        = "MacOS Self Mounting Image";
	website     = "http://fileformats.archiveteam.org/wiki/Apple_Disk_Image";
	idMeta      = ({macFileType, macFileCreator}) => macFileType==="APPL" && macFileCreator==="oneb";
	unsupported = true;
}

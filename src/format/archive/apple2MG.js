import {Format} from "../../Format.js";

export class apple2MG extends Format
{
	name           = "Apple 2MG Disk Image";
	website        = "http://fileformats.archiveteam.org/wiki/Apple_Disk_Image";
	ext            = [".2mg"];
	forbidExtMatch = true;
	magic          = ["2IMG Universal Format disk image", "Apple ][ 2IMG Disk Image"];
	idMeta         = ({macFileType}) => macFileType==="2img";
	converters     = ["cadius", "acx"];
}

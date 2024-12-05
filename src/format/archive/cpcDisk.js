import {Format} from "../../Format.js";

export class cpcDisk extends Format
{
	name           = "Amstrad CPC Disk";
	website        = "http://fileformats.archiveteam.org/wiki/DSK_(CPCEMU)";
	ext            = [".dsk"];
	forbidExtMatch = true;
	magic          = ["Standard CPCEMU style disk image", "Extended CPCEMU style disk image", "Amstrad/Spectrum Extended .DSK data", "CPCEMU Disk image format", "Amstrad/Spectrum .DSK data"];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="cDSK" && macFileCreator==="CPC+";
	converters     = ["cpcxfs", "amstradDSKExplorer"];
}

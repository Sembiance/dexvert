import {Format} from "../../Format.js";

export class teledisk extends Format
{
	name           = "Teledisk Disk Image";
	website        = "http://fileformats.archiveteam.org/wiki/TD0";
	ext            = [".td0"];
	forbidExtMatch = true;
	magic          = ["Teledisk Disk compressed image", "floppy image data (TeleDisk)"];
	converters     = ["td02imd", "dskconv[inType:tele]"];
	post           = dexState => Object.assign(dexState.meta, dexState.ran.find(({programid}) => programid==="td02imd")?.meta || {});
}

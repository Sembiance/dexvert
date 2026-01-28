import {Format} from "../../Format.js";

export class diskExpressSFX extends Format
{
	name           = "Disk Express SFX";
	website        = "http://fileformats.archiveteam.org/wiki/Disk_Express";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Disk Express SFX", "16bit DOS Disk eXPress SFX disk image Executable"];
	converters     = ["deark[module:dskexp]", "diskExpressSFX"];
}

import {Format} from "../../Format.js";

export class diskExpressSFX extends Format
{
	name           = "Disk Express SFX";
	website        = "http://fileformats.archiveteam.org/wiki/Disk_Express";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["16bit DOS Disk eXPress SFX disk image Executable"];
	converters     = ["diskExpressSFX"];
}

import {Format} from "../../Format.js";

export class appleDOSDiskImage extends Format
{
	name           = "Apple DOS Disk Image";
	website        = "http://fileformats.archiveteam.org/wiki/DSK_(Apple_II)";
	ext            = [".dsk"];
	forbidExtMatch = true;
	magic          = [/^Apple DOS .*Image/, /^Apple ProDOS .*Image/, /^Apple II DOS .*disk image/, /^Apple II ProDOS .*disk image/];
	converters     = ["acx"];
}

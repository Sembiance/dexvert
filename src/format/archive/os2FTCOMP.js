import {Format} from "../../Format.js";

export class os2FTCOMP extends Format
{
	name        = "OS/2 FTCOMP Archive";
	website     = "http://fileformats.archiveteam.org/wiki/FTCOMP";
	magic       = ["FTCOMP compressed archive"];
	unsupported = true;
	notes       = "OS/2 packed file. Can be unpackde by UNPACK.EXE or UNPACK2.EXE under OS/2. Available in OS/2 Warp, so I could support these by setting up a QEMU emulated OS/2 machine. Maybe some day.";
}

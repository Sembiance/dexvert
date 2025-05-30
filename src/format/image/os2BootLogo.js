import {Format} from "../../Format.js";

export class os2BootLogo extends Format
{
	name       = "OS/2 Boot Logo";
	website    = "http://fileformats.archiveteam.org/wiki/OS/2_Boot_Logo";
	ext        = [".lgo"];
	magic      = ["deark: os2bootlogo"];
	converters = ["deark[module:os2bootlogo]"];
	verify     = ({meta}) => meta.colorCount>2;
}

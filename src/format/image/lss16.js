import {Format} from "../../Format.js";

export class lss16 extends Format
{
	name       = "Syslinux LSS16";
	website    = "http://fileformats.archiveteam.org/wiki/LSS16";
	ext        = [".lss", ".16"];
	magic      = ["LSS16 SYSLINUX Splash image", "SYSLINUX' LSS16 image data", "deark: lss16"];
	converters = ["deark[module:lss16][matchType:magic]", "nconvert[matchType:magic]"];
}

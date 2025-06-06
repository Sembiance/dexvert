import {Format} from "../../Format.js";

export class squashFS extends Format
{
	name       = "SquashFS Image";
	website    = "http://fileformats.archiveteam.org/wiki/Squashfs";
	ext        = [".squashfs", ".sfs", ".squash"];
	magic      = ["Squashfs filesystem", "SquashSF image file", "Linux squashfs", "application/vnd.squashfs", "Archive: SquashFS"];
	converters = ["unsquashfs", "sevenZip[type:squashfs]"];
}

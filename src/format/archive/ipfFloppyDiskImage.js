import {Format} from "../../Format.js";

export class ipfFloppyDiskImage extends Format
{
	name       = "Interchangeable Preservation Format Floppy Disk Image";
	website    = "http://fileformats.archiveteam.org/wiki/IPF";
	ext        = [".ipf"];
	magic      = ["Interchangeable Preservation Format floppy disk image"];
	converters = ["uaeunp"];	// Note: Haven't found any IPF yet that this can actually handle
}

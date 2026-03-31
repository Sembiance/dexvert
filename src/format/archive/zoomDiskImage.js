import {Format} from "../../Format.js";

export class zoomDiskImage extends Format
{
	name           = "ZOOM Disk Image";
	ext            = [".zom"];
	forbidExtMatch = true;
	magic          = ["Zoom compressed disk image"];
	converters     = ["vibeExtract[renameOut]"];
}

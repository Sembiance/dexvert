import {Format} from "../../Format.js";

export class commodoreDiskImage extends Format
{
	name     = "Commodore Disk Image";
	website  = "http://fileformats.archiveteam.org/wiki/D64";
	ext      = [".d64", ".d81", ".d71", ".g64"];
	magic    = ["D64 Image", "D81 Image", "G64 GCR-encoded Disk Image Format", "G64 1541 raw disk image"];
	fileSize = {
		".d64" : 174_848,
		".d81" : 819_200
	};
	matchFileSize = true;
	converters    = ["c1541", "DirMaster"];
}

import {Format} from "../../Format.js";

export class commodoreDiskImage extends Format
{
	name     = "Commodore Disk Image";
	website  = "http://fileformats.archiveteam.org/wiki/D64";
	ext      = [".d64", ".d81", ".d71", ".g64"];
	magic    = ["D64 Image", "D71 Image", "D81 Image", "GCR Image", "G64 GCR-encoded Disk Image Format", "G64 1541 raw disk image", "Commodore CP/M disk image", "deark: d64", /^fmt\/821( |$)/];
	idMeta   = ({macFileType, macFileCreator}) => macFileType==="DISK" && ["C=64", "Frdo"].includes(macFileCreator);
	fileSize = {
		".d64" : 174_848,
		".d81" : 819_200
	};
	matchFileSize = true;
	converters    = ["c1541", "deark[module:d64][matchType:magic]", "DirMaster"];
}

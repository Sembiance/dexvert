import {Format} from "../../Format.js";

export class ibmSaveDsk extends Format
{
	name           = "IBM SaveDskF SKF Disk Image";
	website        = "http://fileformats.archiveteam.org/wiki/LoadDskF/SaveDskF";
	ext            = [".dsk"];
	forbidExtMatch = true;
	magic          = ["IBM SKF disk image", "floppy image data (IBM SaveDskF", "Archive: SaveDskF", "deark: loaddskf (LoadDskF"];
	converters     = ["sevenZip", "deark[module:loaddskf]"];
}

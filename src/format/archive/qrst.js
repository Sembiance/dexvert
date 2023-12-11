import {Format} from "../../Format.js";

export class qrst extends Format
{
	name       = "Compaq Quick Release Sector Transfer Disk Image";
	website    = "http://fileformats.archiveteam.org/wiki/Quick_Release_Sector_Transfer";
	magic      = ["Compaq QRST disk image"];
	converters = ["dskconv[inType:qrst]"];
}

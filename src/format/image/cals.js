import {Format} from "../../Format.js";

export class cals extends Format
{
	name         = "Computer Aided Acquisition and Logistics Support";
	website      = "http://fileformats.archiveteam.org/wiki/CALS_raster";
	ext          = [".ct1", ".cal", ".ras", ".ct2", ".ct3", ".nif", ".ct4", ".c4"];
	magic        = ["CALS raster bitmap", "CALS Compressed Bitmap", "CALS Raster :cals:", /^x-fmt\/28( |$)/];
	metaProvider = ["image"];
	converters   = ["convert", "nconvert[format:cals]", "canvas5[matchType:magic]", "corelPhotoPaint[matchType:magic]"];
	verify       = ({meta}) => meta.height>1 && meta.width>1;
}

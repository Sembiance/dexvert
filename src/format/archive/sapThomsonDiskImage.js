import {Format} from "../../Format.js";

export class sapThomsonDiskImage extends Format
{
	name           = "SAP Thomson Disk Image";
	website        = "http://nostalgies.thomsonistes.org/transfert.html";
	ext            = [".sap"];
	forbidExtMatch = true;
	magic          = ["SAP Thomson disk image", "application/x-thomson-sap-image"];
	converters     = ["sapfs"];
}

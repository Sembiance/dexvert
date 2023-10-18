import {Format} from "../../Format.js";

export class epocInstallationPackage extends Format
{
	name       = "EPOC Installation Package";
	website    = "http://fileformats.archiveteam.org/wiki/SIS";
	magic      = ["EPOC Installation package", "Symbian installation file"];
	ext        = [".sis"];
	converters = ["deark[module:sis]"];
}

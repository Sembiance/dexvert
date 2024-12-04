import {Format} from "../../Format.js";

export class epocInstallationPackage extends Format
{
	name       = "EPOC Installation Package";
	website    = "http://fileformats.archiveteam.org/wiki/SIS";
	magic      = ["EPOC Installation package", "Symbian installation file", "application/vnd.symbian.install", /^Psion Series 5 Application Installer/];
	ext        = [".sis"];
	converters = ["deark[module:sis]"];
}

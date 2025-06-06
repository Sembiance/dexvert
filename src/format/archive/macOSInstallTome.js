import {Format} from "../../Format.js";

export class macOSInstallTome extends Format
{
	name        = "MacOS Installer Tome";
	website     = "http://fileformats.archiveteam.org/wiki/Tome";
	magic       = ["Mac Installation Tome", "deark: tome"];
	idMeta      = ({macFileType, macFileCreator}) => macFileType==="idcp" && macFileCreator==="kakc";
	converters  = ["deark[mac][module:tome]"];
}

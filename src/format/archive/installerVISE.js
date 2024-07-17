import {Format} from "../../Format.js";

export class installerVISE extends Format
{
	name        = "Installer VISE Package";
	website     = "https://en.wikipedia.org/wiki/Installer_VISE";
	ext         = [".mac"];
	magic       = ["Installer VISE Mac package", "VICE Installer EXE", "Installer: Vise"];
	idMeta      = ({macFileCreator}) => macFileCreator==="VIS3";
	unsupported = true;
}

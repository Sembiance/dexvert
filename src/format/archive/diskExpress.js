import {Format} from "../../Format.js";

export class diskExpress extends Format
{
	name           = "Disk Express";
	website        = "http://fileformats.archiveteam.org/wiki/Disk_Express";
	ext            = [".dxp"];
	forbidExtMatch = true;
	magic          = ["Disk eXPress disk image"];
	weakMagic      = true;
	unsupported    = true;	// Can find samples with: https://discmaster.textfiles.com/search?extension=dxp&detection=4153*
}

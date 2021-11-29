import {Format} from "../../Format.js";

export class installShieldHDR extends Format
{
	name        = "InstallShield HDR";
	website     = "http://fileformats.archiveteam.org/wiki/InstallShield_CAB";
	ext         = [".hdr"];
	magic       = ["InstallShield CAB"];
	weakMagic   = true;
	unsupported = true;
	notes       = "HDR files are meta data for installShieldCAB files and are not processed directly.";

	// In order to be an InstallShield HDR file, it must also have a .cab file
	auxFiles = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.cab`);
}

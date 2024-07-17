import {Format} from "../../Format.js";

export class upxPacked extends Format
{
	name           = "UPX Packed";
	website        = "http://fileformats.archiveteam.org/wiki/UPX";
	ext            = [".exe", ".com"];
	forbidExtMatch = true;
	magic          = ["Packer: UPX", "UPX compressed Win32 Executable", "UPX - NRV compressed", /UPX compressed/];
	packed         = true;
	converters     = ["upx[renameKeepFilename]"];
}

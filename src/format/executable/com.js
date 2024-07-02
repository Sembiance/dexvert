import {Format} from "../../Format.js";

export class com extends Format
{
	name           = "MS-DOS COM Executable";
	website        = "http://fileformats.archiveteam.org/wiki/DOS_executable_(.com)";
	ext            = [".com", ".c0m"];
	forbidExtMatch = true;
	magic          = ["DOS executable (COM", /^COM executable for (MS-)?DOS/, "16bit COM executable", "16bit DOS COM", "ASIC compiled DOS COM", "DOS COM Executable Datei", "Borland Turbo Pascal 3.0x DOS Command"];
	unsupported    = true;
}

// Borland Delphi EXE/DLL extractor in sandbox/app/IDR/
// It's not really needed though, as the delphi forms are usually Resources that get extracted by sevenZip and then handled by my borlandDelphiForm program


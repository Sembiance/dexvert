import {Format} from "../../Format.js";

export class com extends Format
{
	name           = "MS-DOS COM Executable";
	website        = "http://fileformats.archiveteam.org/wiki/DOS_executable_(.com)";
	ext            = [".com", ".c0m"];
	forbidExtMatch = true;
	magic          = [
		// general com types
		"DOS executable (COM", /^COM executable for (MS-)?DOS/, "16bit COM executable", "16bit DOS COM", "DR-DOS executable (COM)",

		// specific com types
		"XEQ executable Command library", "P-Screen COM Screen", "OPTIKS Quick View / Self Scrolling COM", "MIDIPAK audio driver", "16bit COM NoStrAdAmuS - LineZer0 patch", "16bit COM Reanimator Of Lash patch", "8bit CP/M-80 PASCAL/M Command",
		"DESQview/X Print Manager driver", "16bit COM Factor - FoXCoRe crack", "16bit DOS SCRNCH Command", "16bit DOS FontEdit ][ Command",

		// compiled by
		"ASIC compiled DOS COM", /^Borland Turbo Pascal [\d.x]+ DOS Command/, "ZBASIC MS-DOS COM executable", "16bit COM ZBasic compiled"
	];
	unsupported = true;
}

// Borland Delphi EXE/DLL extractor in sandbox/app/IDR/
// It's not really needed though, as the delphi forms are usually Resources that get extracted by sevenZip and then handled by my borlandDelphiForm program


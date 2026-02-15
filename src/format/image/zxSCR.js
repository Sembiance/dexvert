import {Format} from "../../Format.js";

export class zxSCR extends Format
{
	name         = "ZX Spectrum Standard SCR";
	website      = "http://fileformats.archiveteam.org/wiki/SCR_(ZX_Spectrum)";
	magic        = ["Z80 Screen dump :zxscr:"];
	ext          = [".scr"];
	fileSize     = [6912, 6921, 6924, 7396];	// Other sizes from: http://cd.textfiles.com/amigaacs/amigaacs02/Utilities/Shareware/Workbench/DataTypes/ZX_DataType/ZX_DataType.readme
	mimeType     = "image/x-zx-spectrum-standard-screen";
	notes        = "Some files are originally animated (S.O.M. Tetris and lenn1st) but converters don't support this.";
	metaProvider = ["image"];
	converters   = ["recoil2png[format:SCR]", "convert", "nconvert[format:zxscr]", `abydosconvert[format:${this.mimeType}]`];
}

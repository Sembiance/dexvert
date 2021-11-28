import {Format} from "../../Format.js";

export class zxSCR extends Format
{
	name         = "ZX Spectrum Standard SCR";
	website      = "https://zxart.ee/eng/graphics/database/pictureType:standard/";
	ext          = [".scr"];
	fileSize     = 6912;
	mimeType     = "image/x-zx-spectrum-standard-screen";
	notes        = "Some files are originally animated (S.O.M. Tetris and lenn1st) but converters don't support this.";
	metaProvider = ["image"];
	converters   = ["recoil2png", "convert", "nconvert", `abydosconvert[format:${this.mimeType}]`];
}

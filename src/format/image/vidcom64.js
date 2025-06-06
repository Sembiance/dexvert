import {Format} from "../../Format.js";

export class vidcom64 extends Format
{
	name      = "Vidcom 64";
	website   = "http://fileformats.archiveteam.org/wiki/Vidcom_64";
	ext       = [".vid"];
	mimeType  = "image/x-vidcom-64";
	magic     = ["Drazpaint (C64) bitmap", "Vidcom 64 :vid:"];	// Shares same magic identifier as Drazpaint
	weakMagic = true;
	fileSize  = 10050;
	
	// nconvert produces clearer output compared to recoil2png
	converters = ["nconvert[format:vid]", "recoil2png", `abydosconvert[format:${this.mimeType}]`, "view64"];
}

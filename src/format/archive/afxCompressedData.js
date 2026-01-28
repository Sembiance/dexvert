import {Format} from "../../Format.js";

export class afxCompressedData extends Format
{
	name       = "AFX compressed data";
	website    = "http://fileformats.archiveteam.org/wiki/Com2txt";
	magic      = ["AFX compressed data", /^AFX compressed file data/];
	converters = ["deark[module:atari_afx]"];
}

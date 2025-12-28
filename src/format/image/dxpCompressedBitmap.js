import {Format} from "../../Format.js";

export class dxpCompressedBitmap extends Format
{
	name       = "DXP compressed bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/DXP_(image_format)";
	ext        = [".dxp"];
	magic      = ["DXP compressed bitmap", "deark: dxp_image"];
	converters = ["deark[module:dxp_image]"];
}

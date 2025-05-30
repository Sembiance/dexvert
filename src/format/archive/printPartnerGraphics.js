import {Format} from "../../Format.js";

export class printPartnerGraphics extends Format
{
	name       = "PrintPartner Graphics Bitmaps";
	website    = "http://fileformats.archiveteam.org/wiki/PrintPartner";
	ext        = [".gph"];
	magic      = ["PrintPartner Graphic bitmaps", "PrintPartner user created Graphic bitmaps", "deark: pp_gph"];
	converters = ["deark[module:pp_gph]"];
}

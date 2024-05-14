import {Format} from "../../Format.js";

export class hpgl extends Format
{
	name       = "Hewlett-Packard Graphics Language";
	website    = "http://fileformats.archiveteam.org/wiki/HP-GL";
	ext        = [".hpgl"];
	magic      = ["Hewlett-Packard Graphics Language"];
	idMeta     = ({macFileType}) => macFileType==="HPGL";
	converters = ["viewCompanion", "corelPhotoPaint", "canvas[matchType:magic][nonRaster]"];
}

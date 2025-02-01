import {Format} from "../../Format.js";

export class warCraftMap extends Format
{
	name       = "WarCraft 2 Map";
	website    = "http://fileformats.archiveteam.org/wiki/Warcraft_II_PUD";
	ext        = [".pud"];
	magic      = ["WarCraft map (v2)"];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="W2ed" && macFileCreator==="W2ed";
	converters = ["pud"];
}

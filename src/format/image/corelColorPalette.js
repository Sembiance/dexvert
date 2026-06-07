import {Format} from "../../Format.js";

export class corelColorPalette extends Format
{
	name           = "Corel Color Palette";
	ext            = [".cpl"];
	forbidExtMatch = true;
	magic          = ["Corel Color Palette"];
	idMeta         = ({macFileType, macFileCreator}) => macFileType===".CPL" && macFileCreator==="Cdrw";
	converters     = ["uniconvertor"];
}

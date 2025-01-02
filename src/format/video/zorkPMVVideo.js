import {Format} from "../../Format.js";

export class zorkPMVVideo extends Format
{
	name           = "Zork PMV video";
	website        = "https://wiki.multimedia.cx/index.php/Zork_PMV";
	ext            = [".pmv"];
	forbidExtMatch = true;
	magic          = ["Zork PMV Video", "MADE Engine Video"];
	idMeta         = ({macFileType, macFileCreator}) => macFileType===".DAT" && macFileCreator==="RZrk";
	converters     = ["na_game_tool[format:pmv]"];
}

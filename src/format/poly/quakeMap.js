import {Format} from "../../Format.js";

export class quakeMap extends Format
{
	name           = "Quake Map";
	ext            = [".bsp"];
	forbidExtMatch = true;
	magic          = ["Quake Map"];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="QBsp" && macFileCreator==="Quak";
	converters     = ["noesis[type:poly]"];
}

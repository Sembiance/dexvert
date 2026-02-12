import {Format} from "../../Format.js";

export class paxImperiaEminentDomainGameArchive extends Format
{
	name           = "Pax Imperia: Eminent Domain Game Archive";
	ext            = [".img"];
	forbidExtMatch = true;
	magic          = ["Pax Imperia: Eminent Domain game data archive", /^geArchive: IMG_II( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="Px2D" && macFileCreator==="Pax2";
	converters     = ["gameextractor[codes:IMG_II]"];
}

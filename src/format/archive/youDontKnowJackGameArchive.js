import {Format} from "../../Format.js";

export class youDontKnowJackGameArchive extends Format
{
	name           = "You Don't Know Jack Game Archive";
	ext            = [".srf"];
	forbidExtMatch = true;
	magic          = ["You Don't Know Jack game data archive", /^geArchive: SRF_SRF1( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => (macFileType==="srf " && ["SRF ", "YDKJ"].includes(macFileCreator)) || (macFileType==="srf1" && macFileCreator==="SrfM") || (macFileType==="xSRF" && ["C2Bs", "Qbrw"].includes(macFileCreator));
	converters     = ["gameextractor[codes:SRF_SRF1]"];
}

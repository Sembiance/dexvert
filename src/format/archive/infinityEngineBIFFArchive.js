import {Format} from "../../Format.js";

export class infinityEngineBIFFArchive extends Format
{
	name           = "Infinity Engine BIFF Archive";
	ext            = [".bif"];
	forbidExtMatch = true;
	magic          = ["Infinity Engine archive", /^geArchive: (BIF_BIFFV1|BIF_BIFFV11)( |$)/];
	converters     = ["gameextractor[codes:BIF_BIFFV1,BIF_BIFFV11]"];
}

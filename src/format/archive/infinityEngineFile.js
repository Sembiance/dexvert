import {Format} from "../../Format.js";

export class infinityEngineFile extends Format
{
	name           = "Infinity Engine File";
	ext            = [".dlg", ".cre", ".itm", ".are", ".tlk", ".spl", ".sto"];
	forbidExtMatch = true;
	magic          = ["Infinity Engine ", /^geArchive: (BIF_BIFFV1|BIF_BIFFV11)( |$)/];
	converters     = ["gameextractor[codes:BIF_BIFFV1,BIF_BIFFV11]"];
}

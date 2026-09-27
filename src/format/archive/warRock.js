import {Format} from "../../Format.js";

export class warRock extends Format
{
	name           = "War Rock Archive";
	ext            = [".fpk"];
	forbidExtMatch = true;
	magic          = [/^geArchive: FPK_JINDO( |$)/];
	converters     = ["gameextractor[codes:FPK_JINDO]"];
}

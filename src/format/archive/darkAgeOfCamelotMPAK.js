import {Format} from "../../Format.js";

export class darkAgeOfCamelotMPAK extends Format
{
	name           = "Dark Age of Camleot MPAK Game Archive";
	ext            = [".npk", ".mpk"];
	forbidExtMatch = true;
	magic          = [/^geArchive: NPK_MPAK( |$)/];
	converters     = ["gameextractor[codes:NPK_MPAK]"];
}

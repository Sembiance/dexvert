import {Format} from "../../Format.js";

export class quadrupleDArchiverArchive extends Format
{
	name           = "Quadruple D Archiver Archive";
	ext            = [".qda"];
	forbidExtMatch = true;
	magic          = ["Quadruple D Archiver compressed archive", "Pendulumania game data", /^geArchive: QDA_QDA0( |$)/];
	converters     = ["gameextractor[codes:QDA_QDA0]"];
}

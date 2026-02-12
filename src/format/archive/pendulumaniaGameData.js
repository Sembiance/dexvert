import {Format} from "../../Format.js";

export class pendulumaniaGameData extends Format
{
	name           = "Pendulumania game data";
	ext            = [".qda"];
	forbidExtMatch = true;
	magic          = ["Pendulumania game data", /^geArchive: QDA_QDA0( |$)/];
	converters     = ["gameextractor[codes:QDA_QDA0]"];
}

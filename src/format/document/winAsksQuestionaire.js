import {Format} from "../../Format.js";

export class winAsksQuestionaire extends Format
{
	name           = "WinAsks Questionnaire";
	ext            = [".wap", ".wa"];
	forbidExtMatch = true;
	magic          = ["WinAsks Editor Questionnaire"];
	converters     = ["strings"];
}

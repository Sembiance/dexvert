import {Format} from "../../Format.js";

export class visualBasicForm extends Format
{
	name           = "Visual Basic Form";
	website        = "http://fileformats.archiveteam.org/wiki/VisualBasic_form";
	ext            = [".frm"];
	forbidExtMatch = true;
	magic          = ["Visual Basic Form"];
	converters     = ["strings"];
}

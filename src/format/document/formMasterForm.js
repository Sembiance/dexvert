import {Format} from "../../Format.js";

export class formMasterForm extends Format
{
	name           = "Form Master Form";
	ext            = [".frm"];
	forbidExtMatch = true;
	magic          = ["Form Master Form"];
	converters     = ["strings"];
}

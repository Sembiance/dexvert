import {Format} from "../../Format.js";

export class visualXBaseForm extends Format
{
	name           = "Visual XBase Form";
	ext            = [".ww"];
	forbidExtMatch = true;
	magic          = ["Visual XBase form/screen"];
	weakMagic      = true;
	converters     = ["strings"];
}

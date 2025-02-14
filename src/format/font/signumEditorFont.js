import {Format} from "../../Format.js";

export class signumEditorFont extends Format
{
	name           = "Signum! Editor Font";
	ext            = [".e24"];
	forbidExtMatch = true;
	magic          = ["Bitmapped Signum!2 printer font (screen)"];
	converters     = ["chsetKB"];
}

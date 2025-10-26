import {Format} from "../../Format.js";

export class signumEditorFont extends Format
{
	name           = "Signum! Editor Font";
	ext            = [".e24"];
	forbidExtMatch = true;
	magic          = ["Signum!2 bitmapped Editor font"];
	converters     = ["chsetKB"];
}

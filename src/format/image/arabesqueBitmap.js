import {Format} from "../../Format.js";

export class arabesqueBitmap extends Format
{
	name           = "Arabesque bitmap";
	ext            = [".abm", ".puf"];
	forbidExtMatch = true;
	magic          = ["Arabesque Professional bitmapped drawing"];
	converters     = ["wuimg"];
}

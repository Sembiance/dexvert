import {Format} from "../../Format.js";

export class irisShowcase extends Format
{
	name           = "IRIS Showcase Presentation/Drawing";
	ext            = [".sc", ".showcase"];
	forbidExtMatch = true;
	magic          = [/^IRIS Showcase file/, "IRIS Showcase drawing"];
	converters     = ["vibe2pdf"];
}

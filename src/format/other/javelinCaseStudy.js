import {Format} from "../../Format.js";

export class javelinCaseStudy extends Format
{
	name           = "Javelin Case Study";
	ext            = [".cas"];
	forbidExtMatch = true;
	magic          = ["Javelin Case study"];
	converters     = ["strings"];
}

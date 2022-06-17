import {Format} from "../../Format.js";

export class demoManiacScript extends Format
{
	name           = "DemoManiac SCript";
	ext            = [".script"];
	forbidExtMatch = true;
	magic          = ["DemoManiac Script"];
	weakMagic      = true;
	converters     = ["strings"];
}

import {Format} from "../../Format.js";

export class frameMakerBook extends Format
{
	name           = "FrameMaker Book";
	ext            = [".book"];
	forbidExtMatch = true;
	magic          = ["FrameMaker book"];
	converters     = ["strings"];
}

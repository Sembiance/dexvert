import {Format} from "../../Format.js";

export class caimanGraphics extends Format
{
	name           = "Caiman graphics";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = ["Caiman graphics Data"];
	converters     = ["wuimg[format:caiman]"];
}

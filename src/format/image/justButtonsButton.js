import {Format} from "../../Format.js";

export class justButtonsButton extends Format
{
	name           = "JustButtons Button";
	ext            = [".btn"];
	forbidExtMatch = true;
	magic          = ["JustButtons animated bitmap :btn:"];
	converters     = ["nconvert[format:btn][extractAll]"];
}

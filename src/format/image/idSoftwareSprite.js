import {Format} from "../../Format.js";

export class idSoftwareSprite extends Format
{
	name           = "ID Software Sprite";
	ext            = [".spr", ".spr32"];
	forbidExtMatch = true;
	magic          = ["ID Software Sprite format"];
	converters     = ["wuimg[format:idsp]"];
}

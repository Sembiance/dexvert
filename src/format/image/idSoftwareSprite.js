import {Format} from "../../Format.js";

export class idSoftwareSprite extends Format
{
	name           = "ID Software Sprite";
	ext            = [".spr", ".spr32"];
	forbidExtMatch = true;
	magic          = ["ID Software Sprite format", /^geViewer: SXWAD_SPR_IDSP( |$)/];
	converters     = ["wuimg[format:idsp]", "gameextractor[renameOut][codes:SXWAD_SPR_IDSP]"];
}

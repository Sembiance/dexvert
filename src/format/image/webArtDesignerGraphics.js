import {Format} from "../../Format.js";

export class webArtDesignerGraphics extends Format
{
	name           = "WebArt Designer graphics";
	ext            = [".mif"];
	forbidExtMatch = true;
	magic          = ["WebArt Designer graphics"];
	converters     = ["foremost"];
}

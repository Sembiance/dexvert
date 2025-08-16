import {Format} from "../../Format.js";

export class dkAnimation extends Format
{
	name           = "DK Multimedia Animation";
	website        = "https://wiki.multimedia.cx/index.php/DK_Animation";
	ext            = [".ani"];
	forbidExtMatch = true;
	magic          = ["DK Multimedia Animation", "Dorling Kindersley Animation", "DK Animation (dkanim)"];
	converters     = ["na_game_tool[format:dkanim]"];
}

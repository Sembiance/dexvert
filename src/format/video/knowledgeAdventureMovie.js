import {Format} from "../../Format.js";

export class knowledgeAdventureMovie extends Format
{
	name           = "Knowledge Adventure MoVie";
	website        = "https://wiki.multimedia.cx/index.php/Space_Adventure_MOV";
	ext            = [".mov", ".img", ".mv0", ".mv1", ".mv3", ".mv4", ".mv5", ".mv6", ".mv7", ".mv8", ".mv9", ".im0", ".im1", ".im2"];
	forbidExtMatch = true;
	magic          = ["Knowledge Adventure MoVie video", "Knowledge Adventure MOV v2"];
	weakMagic      = ["Knowledge Adventure MOV v2"];
	converters     = ["na_game_tool[format:kamov2]"];
}

import {xu} from "xu";
import {Format} from "../../Format.js";

export class jazzJackrabbit2Video extends Format
{
	name           = "Jazz Jackrabbit 2 Video";
	website        = "https://wiki.multimedia.cx/index.php/Jazz_Jackrabbit_2_J2V";
	ext            = [".j2v"];
	forbidExtMatch = true;
	magic          = ["Jazz Jackrabbit 2 Video"];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="J2VI" && macFileCreator==="Jaz2";
	converters     = ["na_game_tool[format:jazz2]"];
}

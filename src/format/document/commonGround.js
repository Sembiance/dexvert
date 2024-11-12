import {Format} from "../../Format.js";

export class commonGround extends Format
{
	name           = "Common Ground";
	website        = "http://fileformats.archiveteam.org/wiki/Common_Ground";
	ext            = [".dp"];
	forbidExtMatch = true;
	magic          = ["Common Ground Digital Paper document"];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="CGDC" && macFileCreator==="CGVM";
	notes          = "Can probably only be converted properly with the Common Ground software itself, which I was unable to locate.";
	converters     = ["strings"];
}

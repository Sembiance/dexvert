import {Format} from "../../Format.js";

export class concertWare extends Format
{
	name       = "ConcertWare";
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="CWMF" && macFileCreator==="CWMP";
	converters = ["vibe2wav[renameOut]"];
}

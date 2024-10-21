import {Format} from "../../Format.js";

export class flashAuthoringFile extends Format
{
	name           = "Flash Authoring File";
	website        = "http://fileformats.archiveteam.org/wiki/FLA";
	magic          = ["Flash Authoring / source material", "Flash authoring source"];
	weakMagic      = true;
	ext            = [".fla"];
	forbidExtMatch = true;
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="SPA " && macFileCreator==="MFL2";
	notes          = "This can be VASTLY improved by opening these in the original Flash programs that made them, then exporting to SWF and extracting from that. But I tried with Flash 5 and it only opened like 1 out of 5 files, so I'd need to research others.";
	converters     = ["sevenZip", "unar", "deark[module:cfb][opt:cfb:extractstreams]"];
}

import {Format} from "../../Format.js";

export class frontPageThemePack extends Format
{
	name           = "FrontPage Theme-Pack";
	ext            = [".elm"];
	forbidExtMatch = true;
	magic          = ["FrontPage Theme-Pack"];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="THME" && macFileCreator==="MSOF";
	converters     = ["unFrontPageThemePack"];
}

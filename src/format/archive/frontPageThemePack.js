import {Format} from "../../Format.js";

export class frontPageThemePack extends Format
{
	name           = "FrontPage Theme-Pack";
	ext            = [".elm"];
	forbidExtMatch = true;
	magic          = ["FrontPage Theme-Pack"];
	converters     = ["unFrontPageThemePack"];
}

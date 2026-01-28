import {Format} from "../../Format.js";

export class templateCatalogSpinnaker extends Format
{
	name           = "Template Catalog Spinnaker";
	website        = "http://fileformats.archiveteam.org/wiki/Template_Catalog_(Spinnaker_.TCT)";
	ext            = [".tct"];
	forbidExtMatch = true;
	magic          = ["Template Catalog Spinnaker", "deark: tplt_cat_sp (Spinnaker Template Catalog)"];
	converters     = ["deark[module:tplt_cat_sp]"];
}

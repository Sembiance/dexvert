import {Format} from "../../Format.js";

export class pictureCatalogSpinnaker extends Format
{
	name           = "Picture Catalog Spinnaker";
	website        = "http://fileformats.archiveteam.org/wiki/Picture_Catalog_(Spinnaker_.CAT)";
	ext            = [".cat"];
	forbidExtMatch = true;
	magic          = ["Picture Catalog Spinnaker", "deark: pic_cat_sp (spcat)"];
	converters     = ["deark[module:pic_cat_sp]"];
}

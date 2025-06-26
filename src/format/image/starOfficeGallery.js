import {Format} from "../../Format.js";

export class starOfficeGallery extends Format
{
	name           = "Star Office Gallery";
	ext            = [".sdg"];
	forbidExtMatch = true;
	magic          = ["Star Office Gallery :sdg:"];
	converters     = ["nconvert[extractAll][format:sdg]"];
}

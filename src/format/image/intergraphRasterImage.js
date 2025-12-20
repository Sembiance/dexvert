import {Format} from "../../Format.js";

export class intergraphRasterImage extends Format
{
	name           = "Intergrash Raster Image";
	ext            = [".cot", ".cit", ".rle", "rgb", ".res", ".ci", ".4"];
	forbidExtMatch = true;
	magic          = ["Intergraph Raster bitmap", /^Intergraph raster image/, /^Intergraph - Type \d+ :ingr:/];
	converters     = ["nconvert[format:ingr]"];
}

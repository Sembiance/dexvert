import {Format} from "../../Format.js";

export class wavefrontMaterial extends Format
{
	name           = "Wavefront Material";
	website        = "http://fileformats.archiveteam.org/wiki/Wavefront_MTL";
	ext            = [".mtl"];
	forbidExtMatch = true;
	magic          = ["Alias|Wavefront material", /^fmt\/1211( |$)/];
	untouched      = true;
	metaProvider   = ["text"];
}

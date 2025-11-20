import {Format} from "../../Format.js";

export class b3dImage extends Format
{
	name           = "B3D Image";
	ext            = [".b3d"];
	forbidExtMatch = true;
	magic          = ["B3D :b3d:"];
	converters     = ["nconvert[format:b3d] -> convert[removeAlpha]"];
}
